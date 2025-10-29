from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import Optional, List
from pydantic import BaseModel

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, AIContent, Question, QuestionType
from app.services.ai_service import ai_service
from app.services.ocr_service import ocr_service

router = APIRouter()

class GenerateQuestionsRequest(BaseModel):
    material_id: int
    num_questions: int = 10
    difficulty: str = "medium"
    question_types: List[str] = ["multiple_choice", "true_false"]
    test_id: Optional[int] = None

class StudyHelpRequest(BaseModel):
    question: str
    context: str = ""
    student_id: Optional[int] = None

class SummarizeRequest(BaseModel):
    material_id: int
    pages: Optional[dict] = None  # {"start": 1, "end": 5}

@router.post("/upload-material")
async def upload_material(
    file: UploadFile = File(...),
    material_name: Optional[str] = Form(None),
    material_type: str = Form("notes"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Upload PDF or image for OCR extraction"""
    try:
        print(f"\n{'='*60}")
        print(f"📤 Material Upload Request")
        print(f"{'='*60}")
        print(f"User: {user.full_name} (ID: {user.id})")
        print(f"File: {file.filename}")
        print(f"Material Type: {material_type}")
        
        filename = file.filename
        file_content = await file.read()
        material_name = material_name or filename
        
        print(f"File Size: {len(file_content)} bytes")
        
        if filename.lower().endswith('.pdf'):
            print("🔍 Extracting text from PDF...")
            extracted_text = await ocr_service.extract_text_from_pdf(file_content)
        elif filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            print("🔍 Extracting text from image...")
            extracted_text = await ocr_service.extract_text_from_image(file_content)
        else:
            print("❌ Unsupported file type")
            raise HTTPException(
                status_code=400, 
                detail="Unsupported file type. Use PDF or images."
            )
        
        if not extracted_text.strip():
            print("❌ No text extracted")
            raise HTTPException(
                status_code=422, 
                detail="No text could be extracted from the file"
            )
        
        print(f"✅ Extracted {len(extracted_text)} characters")
        print(f"Preview: {extracted_text[:200]}...")
        
        ai_content = AIContent(
            user_id=user.id,
            topic=material_name,
            content_type=material_type,
            content=extracted_text,
            content_metadata={
                "filename": filename, 
                "text_length": len(extracted_text)
            }
        )
        
        db.add(ai_content)
        await db.commit()
        await db.refresh(ai_content)
        
        print(f"✅ Saved to database (ID: {ai_content.id})")
        print(f"{'='*60}\n")
        
        return {
            "id": ai_content.id,
            "topic": ai_content.topic,
            "content_type": ai_content.content_type,
            "content_length": len(extracted_text),
            "created_at": ai_content.created_at.isoformat(),
            "status": "success",
            "message": f"Successfully extracted {len(extracted_text)} characters"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Material upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Material processing failed: {str(e)}"
        )

@router.post("/generate-questions")
async def generate_questions(
    request: GenerateQuestionsRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Generate questions from uploaded material"""
    try:
        print(f"\n{'='*60}")
        print(f"🤖 Question Generation Request")
        print(f"{'='*60}")
        print(f"User: {user.full_name} (ID: {user.id})")
        print(f"Material ID: {request.material_id}")
        print(f"Num Questions: {request.num_questions}")
        print(f"Difficulty: {request.difficulty}")
        print(f"Question Types: {request.question_types}")
        
        result = await db.execute(
            select(AIContent).where(AIContent.id == request.material_id)
        )
        material = result.scalar_one_or_none()
        
        if not material:
            print("❌ Material not found")
            raise HTTPException(status_code=404, detail="Material not found")
        
        print(f"✅ Material found: {material.topic}")
        print(f"   Content length: {len(material.content)} chars")
        
        questions = await ai_service.generate_questions_from_material(
            material.content,
            num_questions=request.num_questions,
            difficulty=request.difficulty,
            question_types=request.question_types
        )
        
        print(f"✅ Generated {len(questions)} questions")
        
        generated_ids = []
        
        if request.test_id:
            print(f"   Saving to test ID: {request.test_id}")
            for idx, q in enumerate(questions):
                q_type = q["type"]
                if q_type == "mcq":
                    q_type = "multiple_choice"
                
                question = Question(
                    test_id=request.test_id,
                    question_text=q["question"],
                    question_type=QuestionType(q_type),
                    options=q.get("options", []),
                    correct_answer=q["correct_answer"],
                    marks=q.get("points", 1),
                    difficulty=request.difficulty,
                    order_index=idx
                )
                db.add(question)
                await db.flush()
                generated_ids.append(question.id)
                print(f"   ✓ Saved question {idx + 1} (ID: {question.id})")
            
            await db.commit()
            print(f"✅ All questions saved to database")
        
        print(f"{'='*60}\n")
        
        return {
            "questions": questions,
            "count": len(questions),
            "question_ids": generated_ids,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Question generation error: {str(e)}")
        import traceback
        traceback.print_exc()
        await db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Question generation failed: {str(e)}"
        )

@router.post("/study-help")
async def study_help(
    request: StudyHelpRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI study help for students"""
    try:
        print(f"📚 Study Help Request from user {user.id}")
        print(f"   Question: {request.question[:100]}...")
        print(f"   Context length: {len(request.context)}")
        print(f"   Student ID: {request.student_id}")
        
        explanation = await ai_service.provide_study_help(
            request.question, 
            request.context
        )
        
        print(f"✅ AI response received ({len(explanation)} chars)")
        
        if request.student_id:
            print(f"   Saving to database for student {request.student_id}")
            study_log = AIContent(
                user_id=request.student_id,
                topic="Study Help",
                content_type="study_help",
                content=explanation,
                content_metadata={
                    "question": request.question, 
                    "context": request.context
                }
            )
            db.add(study_log)
            await db.commit()
            print(f"   ✅ Saved to database")
        
        return {
            "explanation": explanation,
            "status": "success"
        }
        
    except Exception as e:
        import traceback
        print(f"❌ Study help error: {str(e)}")
        print("Full traceback:")
        traceback.print_exc()
        
        await db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"Study help failed: {str(e)}"
        )

@router.post("/summarize")
async def summarize_material(
    request: SummarizeRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get AI summary of material"""
    try:
        print(f"📝 Summary request for material {request.material_id}")
        
        # Get material
        result = await db.execute(
            select(AIContent).where(AIContent.id == request.material_id)
        )
        material = result.scalar_one_or_none()
        
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")
        
        print(f"   Material found: {material.topic}")
        print(f"   Pages: {request.pages}")
        
        # Generate summary
        summary = await ai_service.provide_summary(
            material.content,
            request.pages
        )
        
        print(f"✅ Summary generated ({len(summary)} chars)")
        
        return {
            "summary": summary,
            "material_id": request.material_id,
            "pages": request.pages,
            "status": "success"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"❌ Summary error: {str(e)}")
        traceback.print_exc()
        
        raise HTTPException(
            status_code=500,
            detail=f"Summary generation failed: {str(e)}"
        )

@router.get("/materials/{teacher_id}")
async def get_teacher_materials(
    teacher_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all materials uploaded by a teacher"""
    try:
        result = await db.execute(
            select(AIContent)
            .where(AIContent.user_id == teacher_id)
            .where(AIContent.content_type.in_(["notes", "textbook", "article", "slides"]))
            .order_by(desc(AIContent.created_at))
        )
        materials = result.scalars().all()
        
        materials_list = []
        for material in materials:
            materials_list.append({
                "id": material.id,
                "name": material.topic,
                "type": material.content_type,
                "content_length": len(material.content) if material.content else 0,
                "created_at": material.created_at.isoformat(),
                "teacher_id": material.user_id
            })
        
        return materials_list
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch materials: {str(e)}"
        )

@router.get("/material/{material_id}")
async def get_material(
    material_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get specific material details"""
    try:
        result = await db.execute(
            select(AIContent).where(AIContent.id == material_id)
        )
        material = result.scalar_one_or_none()
        
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")
        
        return {
            "id": material.id,
            "name": material.topic,
            "type": material.content_type,
            "content": material.content,
            "content_length": len(material.content) if material.content else 0,
            "created_at": material.created_at.isoformat(),
            "teacher_id": material.user_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch material: {str(e)}"
        )

@router.delete("/material/{material_id}")
async def delete_material(
    material_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a material"""
    try:
        result = await db.execute(
            select(AIContent).where(AIContent.id == material_id)
        )
        material = result.scalar_one_or_none()
        
        if not material:
            raise HTTPException(status_code=404, detail="Material not found")
        
        # Check if user owns this material
        if material.user_id != user.id and user.role != "admin":
            raise HTTPException(
                status_code=403, 
                detail="Not authorized to delete this material"
            )
        
        await db.delete(material)
        await db.commit()
        
        return {"status": "success", "message": "Material deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete material: {str(e)}"
        )

import json
from typing import List, Dict, Any, Optional
from groq import AsyncGroq
from app.core.config import settings

class AIService:
    def __init__(self):
        self.client = AsyncGroq(api_key=settings.GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"
    
    async def generate_course(
        self,
        topic: str,
        duration_days: int,
        difficulty: str = "medium",
        learning_style: str = "comprehensive"
    ) -> Dict[str, Any]:
        """Generate a complete course with daily lessons and assessments"""
        
        prompt = f"""Create a comprehensive {duration_days}-day course on: {topic}

Difficulty Level: {difficulty}
Learning Style: {learning_style}

Requirements:
1. Break down the course into {duration_days} daily lessons
2. Each day should build upon previous knowledge
3. Include clear learning objectives for each day
4. Suggest practice activities and reading materials
5. Include mini-assessments every few days

Return ONLY a valid JSON object with this structure:
{{
  "course_title": "Course title",
  "description": "Brief course description",
  "difficulty": "{difficulty}",
  "total_days": {duration_days},
  "daily_lessons": [
    {{
      "day": 1,
      "title": "Lesson title",
      "objectives": ["Objective 1", "Objective 2"],
      "topics": ["Topic 1", "Topic 2"],
      "content_summary": "What will be covered",
      "estimated_time": "2-3 hours",
      "resources": ["Resource 1", "Resource 2"],
      "practice_activities": ["Activity 1", "Activity 2"],
      "has_assessment": false
    }}
  ],
  "assessment_days": [3, 7, 14, 21],
  "prerequisites": ["Prerequisite 1", "Prerequisite 2"],
  "learning_outcomes": ["Outcome 1", "Outcome 2"]
}}

Do not include any text outside the JSON object."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert curriculum designer and educational planner. Create structured, progressive learning paths. Always return valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean JSON markers
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        try:
            course_data = json.loads(content)
            return course_data
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse course data: {e}")
    
    async def generate_day_content(
        self,
        topic: str,
        day_number: int,
        lesson_title: str,
        objectives: List[str]
    ) -> str:
        """Generate detailed content for a specific day's lesson"""
        
        objectives_text = "\n".join([f"- {obj}" for obj in objectives])
        
        prompt = f"""Create comprehensive, detailed learning content for Day {day_number} of a course on {topic}.

Lesson Title: {lesson_title}

Learning Objectives:
{objectives_text}

Create a complete lesson with the following structure:

# {lesson_title}

## Introduction
Provide a clear introduction to the day's topic with context and relevance.

## Core Concepts
Explain each concept in detail with:
- Clear definitions
- Real-world analogies
- Practical examples
- Visual descriptions (describe what a diagram would show)

## Detailed Explanations
Break down complex topics into digestible sections:
1. Start with fundamentals
2. Build up complexity gradually
3. Include multiple examples
4. Show common mistakes to avoid

## Practical Examples
Provide 3-5 worked examples with:
- Problem statement
- Step-by-step solution
- Explanation of each step
- Final answer with verification

## Practice Exercises
List 5-7 practice problems for students to try:
- Mix of easy, medium, and hard problems
- Cover all key concepts from the lesson
- Include hints for challenging problems

## Key Takeaways
Summarize the most important points to remember.

## Additional Resources
Suggest books, websites, or videos for further learning.

Write in a clear, engaging, educational style. Make it feel like a textbook chapter that students can actually learn from."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert teacher and educational content creator. Write comprehensive, detailed lesson content that students can actually learn from. Write like a textbook author - thorough, clear, and educational."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4096
        )
        
        return response.choices[0].message.content
    
    async def generate_assessment(
        self,
        topic: str,
        day_number: int,
        covered_topics: List[str],
        num_questions: int = 5,
        difficulty: str = "medium"
    ) -> List[Dict[str, Any]]:
        """Generate assessment questions for topics covered so far"""
        
        topics_text = "\n".join([f"- {t}" for t in covered_topics])
        
        prompt = f"""Generate {num_questions} assessment questions for Day {day_number} of a {topic} course.

Topics covered so far:
{topics_text}

Difficulty: {difficulty}

Requirements:
- Mix of question types (multiple choice, true/false, short answer)
- Test understanding of key concepts
- Progressive difficulty
- Clear, unambiguous questions

Return ONLY a valid JSON array:
[
  {{
    "question_type": "multiple_choice",
    "question_text": "Question text?",
    "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}},
    "correct_answer": "A",
    "marks": 2,
    "explanation": "Why this is correct"
  }},
  {{
    "question_type": "true_false",
    "question_text": "Statement to evaluate",
    "correct_answer": "true",
    "marks": 1,
    "explanation": "Explanation"
  }},
  {{
    "question_type": "short_answer",
    "question_text": "Question requiring brief answer?",
    "correct_answer": "Expected answer",
    "marks": 3,
    "explanation": "Key points to include"
  }}
]"""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert assessment designer. Create fair, comprehensive tests. Return only valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=3000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Clean JSON markers
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        try:
            questions = json.loads(content)
            return questions
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse assessment questions: {e}")
    
    async def generate_learning_content(
        self,
        topic: str,
        content_type: str,
        difficulty: str = "medium"
    ) -> str:
        prompts = {
            "summary": f"Provide a comprehensive {difficulty}-level summary of {topic}. Include key concepts, important points, and examples.",
            "explanation": f"Explain {topic} in detail at a {difficulty} level. Break down complex concepts and provide clear examples.",
            "notes": f"Create detailed study notes on {topic} suitable for {difficulty} level students. Include definitions, key points, and practice tips.",
            "tutorial": f"Write a step-by-step tutorial on {topic} at {difficulty} level. Include examples and practice exercises."
        }
        
        prompt = prompts.get(content_type, prompts["summary"])
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert educational content creator. Provide clear, accurate, and engaging learning content."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        return response.choices[0].message.content
    
    async def generate_quiz_questions(
        self,
        topic: str,
        num_questions: int = 5,
        difficulty: str = "medium"
    ) -> List[Dict[str, Any]]:
        prompt = f"""Generate {num_questions} multiple-choice questions on the topic: {topic}
        
Difficulty level: {difficulty}

Requirements:
- Each question should have 4 options (A, B, C, D)
- Clearly indicate the correct answer
- Questions should test understanding, not just memorization
- Vary the difficulty and depth of questions

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "question_text": "Question here?",
    "options": {{
      "A": "Option A text",
      "B": "Option B text",
      "C": "Option C text",
      "D": "Option D text"
    }},
    "correct_answer": "A",
    "marks": 1,
    "difficulty": "{difficulty}"
  }}
]

Do not include any explanation or text outside the JSON array."""

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert quiz generator. Always return valid JSON arrays only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.8,
            max_tokens=3000
        )
        
        content = response.choices[0].message.content.strip()
        
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        try:
            questions = json.loads(content)
            
            formatted_questions = []
            for q in questions:
                formatted_questions.append({
                    "question_type": "multiple_choice",
                    "question_text": q["question_text"],
                    "options": q["options"],
                    "correct_answer": q["correct_answer"],
                    "marks": q.get("marks", 1),
                    "difficulty": q.get("difficulty", difficulty)
                })
            
            return formatted_questions
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse AI response as JSON: {e}. Content: {content[:200]}")
    
    async def explain_concept(self, concept: str, context: str = "") -> str:
        prompt = f"Explain the concept: {concept}"
        if context:
            prompt += f"\n\nContext: {context}"
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert teacher. Explain concepts clearly and concisely."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    async def generate_questions_from_material(
        self, 
        text_content: str, 
        num_questions: int = 10, 
        difficulty: str = "medium", 
        question_types: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Generate questions from uploaded material text"""
        if not question_types:
            question_types = ["mcq", "true_false", "short_answer"]
        
        type_instructions = self._build_type_instructions(question_types, num_questions)
        
        # Truncate content more aggressively to avoid token limits
        # Keep only first 3000 chars to leave room for response
        content_preview = text_content[:3000] if len(text_content) > 3000 else text_content
        
        prompt = f"""Generate {num_questions} exam questions based on this content.

Content:
{content_preview}

Requirements:
- Difficulty: {difficulty}
- Question types: {', '.join(question_types)}
- For MCQ: provide 4 options with one correct answer
- For True/False: use True or False as correct answer

Return a JSON object with a "questions" array:
{{
  "questions": [
    {{
      "question": "What is the main topic discussed?",
      "type": "mcq",
      "options": ["Option A", "Option B", "Option C", "Option D"],
      "correct_answer": "Option B",
      "explanation": "Brief explanation",
      "points": 2
    }},
    {{
      "question": "The concept of X is fundamental to Y.",
      "type": "true_false",
      "options": ["True", "False"],
      "correct_answer": "True",
      "explanation": "Brief explanation",
      "points": 1
    }}
  ]
}}"""

        try:
            print(f"🤖 Generating {num_questions} questions from material...")
            print(f"   Content length: {len(text_content)} chars")
            print(f"   Difficulty: {difficulty}")
            print(f"   Types: {question_types}")
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert educator. Generate assessment questions in valid JSON format only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2500,  # Reduced to prevent incomplete JSON
                response_format={"type": "json_object"}
            )
            
            content = response.choices[0].message.content.strip()
            print(f"✅ AI response received ({len(content)} chars)")
            
            # Parse JSON response
            try:
                result = json.loads(content)
                
                # Handle different response formats
                if isinstance(result, dict) and "questions" in result:
                    questions = result["questions"]
                elif isinstance(result, list):
                    questions = result
                elif isinstance(result, dict):
                    # Single question wrapped in object
                    questions = [result]
                else:
                    raise ValueError("Unexpected response format")
                
                print(f"✅ Parsed {len(questions)} questions")
                
                # Validate and normalize questions
                normalized_questions = []
                for i, q in enumerate(questions):
                    try:
                        normalized_q = {
                            "question": q.get("question", q.get("question_text", f"Question {i+1}")),
                            "type": q.get("type", "mcq"),
                            "options": q.get("options", []),
                            "correct_answer": q.get("correct_answer", ""),
                            "explanation": q.get("explanation", ""),
                            "points": q.get("points", 2)
                        }
                        normalized_questions.append(normalized_q)
                    except Exception as e:
                        print(f"⚠️  Skipping malformed question {i+1}: {e}")
                        continue
                
                if not normalized_questions:
                    raise ValueError("No valid questions were generated")
                
                print(f"✅ Returning {len(normalized_questions)} normalized questions")
                return normalized_questions
                
            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error: {e}")
                print(f"   Raw content: {content[:500]}...")
                
                # Try to extract JSON from markdown code blocks
                if "```json" in content:
                    start = content.find("```json") + 7
                    end = content.find("```", start)
                    if end > start:
                        content = content[start:end].strip()
                        result = json.loads(content)
                        if isinstance(result, dict) and "questions" in result:
                            return result["questions"]
                        return result if isinstance(result, list) else [result]
                
                raise ValueError(f"Failed to parse JSON response: {e}")
            
        except Exception as e:
            print(f"❌ Question generation error: {str(e)}")
            import traceback
            traceback.print_exc()
            raise Exception(f"Question generation failed: {str(e)}")
    
    async def provide_study_help(self, question: str, context: str = "") -> str:
        """Provide study help for students"""
        prompt = f"""You are a helpful tutor. A student needs help with the following:

Question: {question}

{f"Context: {context[:2000]}" if context else ""}

Provide:
1. A clear explanation
2. Step-by-step breakdown if applicable
3. Key concepts to understand
4. Related topics to study

Keep your response concise but thorough."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a patient, knowledgeable tutor who explains concepts clearly and encourages learning."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Study help generation failed: {str(e)}")
    
    async def provide_summary(self, content: str, pages: Optional[Dict[str, int]] = None) -> str:
        """Provide a comprehensive summary of material"""
        page_info = f"Pages {pages['start']}-{pages['end']}" if pages else "Full document"
        
        prompt = f"""Provide a comprehensive summary of the following material:

{page_info}
Content:
{content[:8000]}

Your summary should include:
1. **Main Topic/Theme**
2. **Key Concepts** (bulleted list)
3. **Important Details** (3-5 points)
4. **Takeaways** (what students should remember)

Format your response in markdown with clear headings and bullet points."""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at creating clear, comprehensive summaries of educational material. Always format output in markdown."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Summary generation failed: {str(e)}")
    
    def _build_type_instructions(self, question_types: List[str], num_questions: int) -> str:
        """Helper to build question type distribution"""
        counts = {}
        base = num_questions // len(question_types)
        remainder = num_questions % len(question_types)
        
        for i, qtype in enumerate(question_types):
            counts[qtype] = base + (1 if i < remainder else 0)
        
        return ", ".join([f"{count} {qtype}" for qtype, count in counts.items()])

ai_service = AIService()

import os
import asyncio
from io import BytesIO
from PIL import Image
import PyPDF2
import pytesseract
from pdf2image import convert_from_bytes
import os

class OCRService:
    def __init__(self):
        # Set Tesseract path from environment variable or use default
        tesseract_path = os.getenv(r'TESSERACT_CMD')
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
        print(f"Tesseract initialized at: {tesseract_path}")
    
    async def extract_text_from_pdf(self, pdf_bytes):
        try:
            print(f" Starting PDF text extraction ({len(pdf_bytes)} bytes)")
            
            # First try extracting text directly from PDF using PyPDF2
            pdf_file = BytesIO(pdf_bytes)
            reader = PyPDF2.PdfReader(pdf_file)
            
            print(f"   PDF has {len(reader.pages)} pages")
            
            all_text = []
            
            for page_num, page in enumerate(reader.pages):
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        all_text.append(f"--- Page {page_num + 1} ---\n{text}")
                        print(f"   ✓ Extracted text from page {page_num + 1} ({len(text)} chars)")
                    else:
                        print(f"   ⚠ No text on page {page_num + 1}")
                except Exception as page_error:
                    print(f"   ❌ Error on page {page_num + 1}: {page_error}")
                    continue
            
            extracted_text = "\n\n".join(all_text)
            
            print(f"✅ PyPDF2 extracted {len(extracted_text)} total characters")
            
            # Only try image conversion if we have Poppler installed
            # This is optional - if PyPDF2 extracted text, we can use that
            try:
                print("   🔄 Attempting OCR with Tesseract...")
                images = convert_from_bytes(pdf_bytes, dpi=200)
                
                if images and len(images) > 0:
                    print(f"   Converted to {len(images)} images")
                    loop = asyncio.get_event_loop()
                    ocr_results = []
                    
                    for idx, img in enumerate(images[:10]):  # Limit to 10 pages
                        print(f"   Processing image {idx + 1}...")
                        ocr_text = await loop.run_in_executor(
                            None, 
                            self._process_single_image, 
                            img
                        )
                        if ocr_text and ocr_text.strip():
                            ocr_results.append(f"--- Page {idx + 1} OCR ---\n{ocr_text}")
                            print(f"   ✓ OCR extracted {len(ocr_text)} chars from page {idx + 1}")
                    
                    if ocr_results:
                        extracted_text += "\n\n" + "\n\n".join(ocr_results)
                        print(f" OCR added {len('\\n\\n'.join(ocr_results))} additional characters")
            except Exception as poppler_error:
                # Poppler not available, but that's okay if we got text from PyPDF2
                print(f" PDF to image conversion skipped (Poppler not available): {str(poppler_error)}")
                if not extracted_text.strip():
                    raise Exception("Could not extract text from PDF. Please install Poppler for image-based OCR.")
            
            if not extracted_text.strip():
                print(" No text extracted from PDF")
                raise Exception("No text could be extracted from the PDF. The PDF may be empty or contain only images without OCR.")
            
            print(f" Total extracted text: {len(extracted_text)} characters")
            return extracted_text
            
        except Exception as e:
            if "No text could be extracted" in str(e) or "Could not extract text" in str(e):
                raise
            print(f" PDF extraction failed: {str(e)}")
            raise Exception(f"PDF extraction failed: {str(e)}")
    
    async def extract_text_from_image(self, image_bytes):
        try:
            img = Image.open(BytesIO(image_bytes)).convert("RGB")
            
            loop = asyncio.get_event_loop()
            ocr_text = await loop.run_in_executor(
                None, 
                self._process_single_image, 
                img
            )
            
            return ocr_text
            
        except Exception as e:
            raise Exception(f"Image extraction failed: {str(e)}")
    
    def _process_single_image(self, pil_image):
        try:
            # Use Tesseract to extract text
            text = pytesseract.image_to_string(pil_image, lang='eng')
            return text if text else ""
            
        except Exception as e:
            print(f" OCR Error: {str(e)}")
            return ""

ocr_service = OCRService()

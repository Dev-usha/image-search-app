import os
import io
import tempfile
from typing import Dict, Any, List
from fastapi import UploadFile
import pytesseract
from PIL import Image
import PyPDF2
import docx
import requests
import json

class MedicalProcessor:
    def __init__(self, ollama_url="http://localhost:11434", summarization_model="mistral"):
        """
        Initialize medical document processor
        
        Args:
            ollama_url: URL of Ollama API for summarization
            summarization_model: Model to use for medical summarization
        """
        self.ollama_url = ollama_url
        self.summarization_model = summarization_model
        
        # Supported file types
        self.supported_types = {
            'image': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'],
            'pdf': ['.pdf'],
            'document': ['.docx', '.doc', '.txt']
        }
        
    async def process_upload(self, file: UploadFile) -> Dict[str, Any]:
        """
        Process uploaded medical document
        
        Args:
            file: Uploaded file from FastAPI
            
        Returns:
            Dictionary with extracted text, summary, and metadata
        """
        try:
            # Read file content
            content = await file.read()
            file_extension = os.path.splitext(file.filename.lower())[1]
            
            # Determine file type and extract text
            extracted_text = ""
            file_type = self._get_file_type(file_extension)
            
            if file_type == "image":
                extracted_text = self._extract_text_from_image(content)
            elif file_type == "pdf":
                extracted_text = self._extract_text_from_pdf(content)
            elif file_type == "document":
                extracted_text = self._extract_text_from_document(content, file_extension)
            else:
                raise ValueError(f"Unsupported file type: {file_extension}")
                
            # Clean and validate extracted text
            extracted_text = self._clean_text(extracted_text)
            
            if not extracted_text.strip():
                raise ValueError("No text could be extracted from the document")
                
            # Generate medical summary
            summary = self._generate_medical_summary(extracted_text)
            
            # Extract key medical information
            medical_info = self._extract_medical_info(extracted_text)
            
            return {
                "extracted_text": extracted_text,
                "summary": summary,
                "medical_info": medical_info,
                "file_type": file_type,
                "original_filename": file.filename,
                "text_length": len(extracted_text)
            }
            
        except Exception as e:
            print(f"Error processing medical upload: {e}")
            raise e
            
    def _get_file_type(self, extension: str) -> str:
        """Determine file type category from extension"""
        for file_type, extensions in self.supported_types.items():
            if extension in extensions:
                return file_type
        return "unknown"
        
    def _extract_text_from_image(self, content: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            # Load image
            image = Image.open(io.BytesIO(content))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            # Perform OCR
            text = pytesseract.image_to_string(image, config='--psm 6')
            
            return text
            
        except Exception as e:
            print(f"Error extracting text from image: {e}")
            return ""
            
    def _extract_text_from_pdf(self, content: bytes) -> str:
        """Extract text from PDF document"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
                
            return text
            
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
            
    def _extract_text_from_document(self, content: bytes, extension: str) -> str:
        """Extract text from document files"""
        try:
            if extension == '.docx':
                doc = docx.Document(io.BytesIO(content))
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return text
                
            elif extension in ['.txt', '.doc']:
                # For .txt and basic .doc files
                return content.decode('utf-8', errors='ignore')
                
            else:
                return ""
                
        except Exception as e:
            print(f"Error extracting text from document: {e}")
            return ""
            
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        if not text:
            return ""
            
        # Remove excessive whitespace
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if line:  # Skip empty lines
                cleaned_lines.append(line)
                
        # Join lines with single newlines
        cleaned_text = '\n'.join(cleaned_lines)
        
        # Remove excessive spaces
        cleaned_text = ' '.join(cleaned_text.split())
        
        return cleaned_text
        
    def _generate_medical_summary(self, text: str) -> str:
        """Generate medical summary using LLM"""
        try:
            prompt = f"""Please provide a concise medical summary of the following document. Focus on:
- Key diagnoses or conditions mentioned
- Important test results or measurements
- Medications or treatments
- Recommendations or follow-up actions
- Any concerning findings

Medical Document:
{text}

Medical Summary:"""

            response = self._call_ollama_for_summary(prompt)
            return response
            
        except Exception as e:
            print(f"Error generating medical summary: {e}")
            return "Summary generation failed. Please review the extracted text manually."
            
    def _extract_medical_info(self, text: str) -> Dict[str, Any]:
        """Extract structured medical information from text"""
        medical_info = {
            "diagnoses": [],
            "medications": [],
            "test_results": [],
            "dates": [],
            "providers": [],
            "recommendations": []
        }
        
        try:
            text_lower = text.lower()
            
            # Common medical keywords to look for
            diagnosis_keywords = ['diagnosis', 'condition', 'disease', 'syndrome', 'disorder']
            medication_keywords = ['medication', 'drug', 'prescription', 'tablet', 'capsule', 'mg', 'ml']
            test_keywords = ['test', 'result', 'lab', 'blood', 'urine', 'x-ray', 'mri', 'ct scan']
            
            # Simple keyword extraction (can be enhanced with NLP)
            lines = text.split('\n')
            
            for line in lines:
                line_lower = line.lower()
                
                # Look for diagnoses
                if any(keyword in line_lower for keyword in diagnosis_keywords):
                    medical_info["diagnoses"].append(line.strip())
                    
                # Look for medications
                if any(keyword in line_lower for keyword in medication_keywords):
                    medical_info["medications"].append(line.strip())
                    
                # Look for test results
                if any(keyword in line_lower for keyword in test_keywords):
                    medical_info["test_results"].append(line.strip())
                    
            # Remove duplicates and limit results
            for key in medical_info:
                medical_info[key] = list(set(medical_info[key]))[:5]  # Limit to 5 items each
                
        except Exception as e:
            print(f"Error extracting medical info: {e}")
            
        return medical_info
        
    def _call_ollama_for_summary(self, prompt: str) -> str:
        """Call Ollama API for medical summarization"""
        try:
            url = f"{self.ollama_url}/api/generate"
            
            payload = {
                "model": self.summarization_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for medical accuracy
                    "top_p": 0.8,
                    "max_tokens": 300
                }
            }
            
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result.get('response', '').strip()
            
        except Exception as e:
            print(f"Error calling Ollama for summary: {e}")
            return "Unable to generate summary at this time."
            
    def validate_medical_document(self, text: str) -> Dict[str, Any]:
        """Validate if document appears to be medical-related"""
        medical_keywords = [
            'patient', 'diagnosis', 'treatment', 'medication', 'doctor', 'physician',
            'hospital', 'clinic', 'medical', 'health', 'prescription', 'lab', 'test',
            'result', 'blood', 'pressure', 'temperature', 'heart', 'symptoms'
        ]
        
        text_lower = text.lower()
        found_keywords = [keyword for keyword in medical_keywords if keyword in text_lower]
        
        is_medical = len(found_keywords) >= 3  # Require at least 3 medical keywords
        confidence = min(len(found_keywords) / 10.0, 1.0)  # Confidence score 0-1
        
        return {
            "is_medical": is_medical,
            "confidence": confidence,
            "found_keywords": found_keywords,
            "keyword_count": len(found_keywords)
        }
        
    def get_supported_formats(self) -> Dict[str, List[str]]:
        """Get list of supported file formats"""
        return self.supported_types.copy()
        
    def estimate_processing_time(self, file_size_mb: float, file_type: str) -> int:
        """Estimate processing time in seconds"""
        base_times = {
            "image": 5,     # OCR takes time
            "pdf": 2,       # Text extraction is fast
            "document": 1   # Direct text access
        }
        
        base_time = base_times.get(file_type, 3)
        
        # Add time based on file size
        size_factor = max(1, file_size_mb / 10)  # 10MB baseline
        
        estimated_time = int(base_time * size_factor)
        return min(estimated_time, 120)  # Cap at 2 minutes
import PyPDF2
import os
from datetime import datetime
import re
from collections import Counter
import json
from typing import Dict, List, Any
from openai_analyzer import OpenAIResumeAnalyzer

class PDFProcessor:
    def __init__(self, analyzer: OpenAIResumeAnalyzer | None = None):
        self.supported_formats = [".pdf"]
        # Allow dependency injection for easier testing
        self.analyzer = analyzer or OpenAIResumeAnalyzer()
        
    def validate_file(self, filename):
        """Validate if the file is a supported PDF format"""
        return os.path.splitext(filename)[1].lower() in self.supported_formats
    
    def extract_text(self, filepath):
        """Extract text from PDF file"""
        try:
            with open(filepath, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    # The heavy-lifting is now done by `OpenAIResumeAnalyzer`.  The kept stub is
    # only here to avoid breaking imports if other modules still reference it.
    def analyze_with_openai(self, text: str) -> Dict[str, Any]:
        return self.analyzer.analyse(text)
    
    def analyze_resume(self, filepath: str) -> Dict[str, Any]:
        """Analyze the resume content using OpenAI"""
        text = self.extract_text(filepath)
        
        try:
            return self.analyzer.analyse(text)
        except Exception as e:
            # Fallback to basic analysis if OpenAI fails
            print(f"OpenAI analysis failed: {str(e)}")
            return self.basic_analysis(text)
    
    def basic_analysis(self, text: str) -> Dict[str, Any]:
        """Fallback to basic analysis if OpenAI fails"""
        technical_skills = []
        soft_skills = []
        
        # Basic skill detection
        technical_skills = re.findall(r'\b(?:python|java|javascript|c\+\+|sql|aws|docker|git|linux)\b', text, re.IGNORECASE)
        soft_skills = re.findall(r'\b(?:communication|teamwork|leadership|problem solving)\b', text, re.IGNORECASE)
        
        # Basic experience detection
        experience = re.search(r'(\d+)\s+years?\s+of\s+experience', text, re.IGNORECASE)
        years_of_experience = int(experience.group(1)) if experience else 0
        
        return {
            'skills': {
                'technical': list(set(technical_skills)),
                'soft': list(set(soft_skills))
            },
            'experience': {
                'years': years_of_experience,
                'industries': []
            },
            'education': [],
            'recommendations': [
                "Consider using OpenAI for more accurate analysis"
            ],
            'analysis_date': datetime.utcnow().isoformat()
        }

    def extract_profile_picture(self, filepath: str):
        """Extract the first image found in the PDF and return it as (bytes, ext).

        This naive implementation assumes the first embedded raster image
        corresponds to the candidate's profile picture.  The method relies on
        PyMuPDF (package name `PyMuPDF`, import name `fitz`) for robust image
        extraction.  If the library is not installed the caller will receive an
        informative exception so that the API layer can surface a clear error
        message.
        """
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise Exception(
                "PyMuPDF is required for profile-picture extraction. Add `PyMuPDF` to your dependencies."
            )

        try:
            doc = fitz.open(filepath)
            for page in doc:
                images = page.get_images(full=True)
                if not images:
                    continue
                # pick the first image entry -> (xref, smask, width, height, bpc, colorspace, alt, name, filter)
                xref = images[0][0]
                base_image = doc.extract_image(xref)
                return base_image["image"], base_image["ext"]

            # If we reach here, no images were found
            raise Exception("No images found in the provided PDF.")
        finally:
            doc.close()

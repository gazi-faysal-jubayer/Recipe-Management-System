"""
Image parser for extracting recipe text using OCR
"""
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import io
from typing import Optional, Tuple
import numpy as np
import cv2
from .text_parser import RecipeTextParser, ParsedRecipe


class RecipeImageParser:
    """Parse recipe images using OCR and LLM"""
    
    def __init__(self, text_parser: Optional[RecipeTextParser] = None):
        self.text_parser = text_parser or RecipeTextParser()
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        # Convert to numpy array
        img_array = np.array(image)
        
        # Convert to grayscale if not already
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Apply denoising
        denoised = cv2.fastNlDenoising(gray, h=30)
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Convert back to PIL Image
        processed_image = Image.fromarray(thresh)
        
        # Enhance contrast
        enhancer = ImageEnhance.Contrast(processed_image)
        processed_image = enhancer.enhance(2)
        
        # Apply sharpening
        processed_image = processed_image.filter(ImageFilter.SHARPEN)
        
        return processed_image
    
    def extract_text(self, image: Image.Image, preprocess: bool = True) -> str:
        """
        Extract text from image using OCR
        
        Args:
            image: PIL Image object
            preprocess: Whether to preprocess the image
            
        Returns:
            Extracted text
        """
        if preprocess:
            image = self.preprocess_image(image)
        
        # Configure Tesseract
        custom_config = r'--oem 3 --psm 6'
        
        try:
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image, config=custom_config)
            
            # Clean up the text
            text = self._clean_ocr_text(text)
            
            return text
        except Exception as e:
            raise Exception(f"OCR extraction failed: {str(e)}")
    
    def _clean_ocr_text(self, text: str) -> str:
        """
        Clean up OCR-extracted text
        
        Args:
            text: Raw OCR text
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        # Remove lines that are mostly garbage characters
        cleaned_lines = []
        for line in lines:
            # Count alphanumeric characters
            alnum_count = sum(c.isalnum() or c.isspace() for c in line)
            if alnum_count / len(line) > 0.7:  # At least 70% readable
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def parse_image(self, image_path: str) -> Tuple[ParsedRecipe, str]:
        """
        Parse recipe from image file
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (ParsedRecipe, extracted_text)
        """
        # Open image
        image = Image.open(image_path)
        
        # Extract text
        extracted_text = self.extract_text(image)
        
        if not extracted_text.strip():
            raise Exception("No text could be extracted from the image")
        
        # Parse extracted text
        parsed_recipe = self.text_parser.parse(extracted_text)
        
        return parsed_recipe, extracted_text
    
    def parse_image_bytes(self, image_bytes: bytes) -> Tuple[ParsedRecipe, str]:
        """
        Parse recipe from image bytes
        
        Args:
            image_bytes: Image file bytes
            
        Returns:
            Tuple of (ParsedRecipe, extracted_text)
        """
        # Open image from bytes
        image = Image.open(io.BytesIO(image_bytes))
        
        # Extract text
        extracted_text = self.extract_text(image)
        
        if not extracted_text.strip():
            raise Exception("No text could be extracted from the image")
        
        # Parse extracted text
        parsed_recipe = self.text_parser.parse(extracted_text)
        
        return parsed_recipe, extracted_text
    
    def extract_text_regions(self, image: Image.Image) -> list:
        """
        Extract text regions with their bounding boxes
        
        Args:
            image: PIL Image object
            
        Returns:
            List of dictionaries with text and coordinates
        """
        # Get detailed OCR data
        data = pytesseract.image_to_data(
            image, 
            output_type=pytesseract.Output.DICT,
            config='--oem 3 --psm 6'
        )
        
        regions = []
        n_boxes = len(data['level'])
        
        for i in range(n_boxes):
            if int(data['conf'][i]) > 30:  # Confidence threshold
                text = data['text'][i].strip()
                if text:
                    regions.append({
                        'text': text,
                        'x': data['left'][i],
                        'y': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i],
                        'confidence': data['conf'][i]
                    })
        
        return regions

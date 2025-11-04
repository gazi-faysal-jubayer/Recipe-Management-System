"""
Standalone OCR script for recipe images
"""
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import sys
import os


def preprocess_image(image_path):
    """Preprocess image for better OCR"""
    img = Image.open(image_path)
    
    # Convert to grayscale
    img = img.convert('L')
    
    # Enhance contrast
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(2)
    
    # Sharpen
    img = img.filter(ImageFilter.SHARPEN)
    
    return img


def extract_recipe_text(image_path, output_file=None):
    """
    Extract text from recipe image
    
    Args:
        image_path: Path to image file
        output_file: Optional output file path
        
    Returns:
        Extracted text
    """
    print(f"Processing: {image_path}")
    
    # Preprocess
    img = preprocess_image(image_path)
    
    # Extract text
    text = pytesseract.image_to_string(img, config='--oem 3 --psm 6')
    
    # Clean text
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    cleaned_text = '\n'.join(lines)
    
    # Save to file if specified
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        print(f"Saved to: {output_file}")
    
    return cleaned_text


def batch_extract(image_folder, output_folder='output'):
    """
    Extract text from all images in a folder
    
    Args:
        image_folder: Folder containing images
        output_folder: Folder to save text files
    """
    os.makedirs(output_folder, exist_ok=True)
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif']
    
    for filename in os.listdir(image_folder):
        if any(filename.lower().endswith(ext) for ext in image_extensions):
            image_path = os.path.join(image_folder, filename)
            output_path = os.path.join(
                output_folder,
                os.path.splitext(filename)[0] + '.txt'
            )
            
            try:
                extract_recipe_text(image_path, output_path)
                print(f"✓ Processed: {filename}")
            except Exception as e:
                print(f"✗ Failed: {filename} - {str(e)}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Single file: python recipe_ocr.py image.jpg [output.txt]")
        print("  Batch mode:  python recipe_ocr.py --batch image_folder [output_folder]")
        sys.exit(1)
    
    if sys.argv[1] == '--batch':
        if len(sys.argv) < 3:
            print("Error: Folder path required for batch mode")
            sys.exit(1)
        
        input_folder = sys.argv[2]
        output_folder = sys.argv[3] if len(sys.argv) > 3 else 'output'
        batch_extract(input_folder, output_folder)
    else:
        image_path = sys.argv[1]
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        
        text = extract_recipe_text(image_path, output_file)
        
        if not output_file:
            print("\n" + "="*50)
            print("EXTRACTED TEXT:")
            print("="*50)
            print(text)

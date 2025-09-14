from PIL import Image

def image_to_pdf(image_path, output_pdf_path):
    """
    Converts an image to PDF.

    :param image_path: Path to the input image file
    :param output_pdf_path: Path to save the output PDF
    """
    # Open the image
    image = Image.open(image_path)
    
    # Convert to RGB (required for PDF)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    
    # Save as PDF
    image.save(output_pdf_path, "PDF")
    print(f"PDF saved at: {output_pdf_path}")
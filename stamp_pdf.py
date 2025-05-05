import io
from pathlib import Path

from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from pypdf import PdfWriter, PdfReader


def stamp_pdf(filename, stamp_image_path="./assets/stamp.png", scale=0.35):
    """
    Adds an image (stamp) to an existing PDF file.

    Args:
        stamp_image_path: Path to the stamp image file (e.g., PNG).        
        scale: Scaling factor for the stamp image.
    Internal:
        input_pdf_path: Path to the input PDF file.
        output_pdf_path: Path to the output PDF file.
    """

    # Construct the input PDF path
    input_pdf_path = Path("./notas") / f"{filename}.pdf"

    output_pdf_path = Path("./out") / f"_{filename}.pdf"
    # Read the existing PDF
    try:
        input_pdf = PdfReader(input_pdf_path)
    except FileNotFoundError:
        print(f"Error: Input PDF file not found: {input_pdf_path}")
        return
    except Exception as e:
        print(f"Error: Could not read input PDF: {e}")
        return

    output_pdf = PdfWriter()

    # Get image dimensions
    try:
        img = Image.open(stamp_image_path)
    except FileNotFoundError:
        print(f"Error: Stamp image file not found: {stamp_image_path}")
        return
    except Exception as e:
        print(f"Error: Could not open stamp image: {e}")
        return

    img_width, img_height = img.size
    scaled_width = img_width * scale
    scaled_height = img_height * scale

    for page_num in range(len(input_pdf.pages)):
        page = input_pdf.pages[page_num]

        # Create a new PDF canvas to hold the stamp
        packet = io.BytesIO()
        # You may need to adjust pagesize
        can = canvas.Canvas(packet, pagesize=letter)
        # Determine page size and calculate center position
        page_width = float(page.mediabox[2])
        page_height = float(page.mediabox[3])
        x_pos = (page_width - scaled_width) / 2 + 90
        y_pos = (page_height - scaled_height) / 2 - 10
        print(
            f"Processing page {page_num + 1}: x_pos = {x_pos}, y_pos = {y_pos}...")
        try:
            can.drawImage(
                stamp_image_path,
                x_pos,
                y_pos,
                width=scaled_width,
                height=scaled_height,
                mask="auto"
            )
            can.save()
        except Exception as e:
            print(f"Error drawing image on canvas: {e}")
            continue  # Try to process remaining pages

        # Move to the beginning of the buffer
        packet.seek(0)
        stamp_pdf_reader = PdfReader(packet)

        # Merge the stamp with the existing page
        try:
            page.merge_page(stamp_pdf_reader.pages[0])
        except Exception as e:
            print(f"Error merging stamp with page: {e}")
            continue  # Try to process remaining pages
        output_pdf.add_page(page)

    # Write the output PDF
    try:
        with open(output_pdf_path, "wb") as output_file:
            output_pdf.write(output_file)
    except Exception as e:
        print(f"Error writing output PDF: {e}")
        return

    print(f"Stamped PDF created: {output_pdf_path}")


def list_filenames_in_notas():
    """
    Lists all files in the ./notas subdirectory and extracts their names (without path or extension).

    Returns:
        list: A list of filenames (without extensions) found in ./notas.
    """
    # Define the path to the ./notas directory
    notas_dir = Path("./notas")

    # Check if the directory exists
    if not notas_dir.exists():
        print(f"Error: Directory {notas_dir} does not exist.")
        return []

    # Get all files in the ./notas directory
    filenames = [file.stem for file in notas_dir.glob(
        "*.pdf") if file.is_file()]

    # Print the filenames
    if filenames:
        print("Notas presentes em ./notas:")
        for name in filenames:
            print(name + " :")
            stamp_pdf(name)
    else:
        print("No files found in ./notas.")

    # return filenames


if __name__ == "__main__":
    # Example usage
    input_pdf_path = "1842"  # Replace with your input PDF
    # stamp_image_path = "stamp.png"  # Replace with your stamp image

    # stamp_pdf(input_pdf_path, stamp_image_path, scale=0.35)

    list_filenames_in_notas()

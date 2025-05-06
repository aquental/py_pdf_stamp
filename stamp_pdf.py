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
        filename (str): The base name of the PDF file to stamp.
        stamp_image_path (str): Path to the stamp image file (e.g., PNG).
        scale (float): Scaling factor for the stamp image.

    Internal:
        input_pdf_path (Path): Path to the input PDF file.
        output_pdf_path (Path): Path to the output PDF file.
    """

    # Construct the input PDF path
    input_pdf_path = Path("./notas") / f"{filename}.pdf"
    output_pdf_path = Path("./out") / f"{filename}.pdf"

    # Read the existing PDF
    try:
        input_pdf = PdfReader(input_pdf_path)
    except FileNotFoundError:
        print(f"Erro: PDF não encontrado : {input_pdf_path}")
        return
    except Exception as e:
        print(f"Erro: Não foi possível ler : {e}")
        return

    output_pdf = PdfWriter()

    # Get image dimensions
    try:
        img = Image.open(stamp_image_path)
    except FileNotFoundError:
        print(f"Erro: Assinatura não encontrada: {stamp_image_path}")
        return
    except Exception as e:
        print(f"Erro: Não consegui abrir a assinatura: {e}")
        return

    img_width, img_height = img.size
    scaled_width = img_width * scale
    scaled_height = img_height * scale

    # Process each page of the input PDF
    for page_num in range(len(input_pdf.pages)):
        page = input_pdf.pages[page_num]

        # Create a new PDF canvas to hold the stamp
        packet = io.BytesIO()
        can = canvas.Canvas(packet, pagesize=letter)

        # Determine page size and calculate center position
        page_width = float(page.mediabox[2])
        page_height = float(page.mediabox[3])
        x_pos = (page_width - scaled_width) / 2 + 90
        y_pos = (page_height - scaled_height) / 2 - 10
        # print(
        #     f"Processing page {page_num + 1}: x_pos = {x_pos}, y_pos = {y_pos}...")

        try:
            # Draw the image onto the canvas
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
            print(f"Erro ao desenhar assinatura: {e}")
            continue  # Try to process remaining pages

        # Move to the beginning of the buffer
        packet.seek(0)
        stamp_pdf_reader = PdfReader(packet)

        # Merge the stamp with the existing page
        try:
            page.merge_page(stamp_pdf_reader.pages[0])
        except Exception as e:
            print(f"Erro ao mesclar assinatura com a página : {e}")
            continue  # Try to process remaining pages

        # Add the page to the output PDF
        output_pdf.add_page(page)

    # Write the output PDF
    try:
        with open(output_pdf_path, "wb") as output_file:
            output_pdf.write(output_file)
    except Exception as e:
        print(f"Erro ao escrever saida PDF: {e}")
        return

    # print(f"PDF assinado com sucesso: {output_pdf_path}")


def stamp_filenames():
    """
    Lists all files in the ./notas subdirectory and extracts their names (without path or extension).

    Returns:
        list: A list of filenames (without extensions) found in ./notas.
    """
    # Define the path to the ./notas directory
    notas_dir = Path("./notas")

    # Check if the directory exists
    if not notas_dir.exists():
        print(f"Erro: diretório {notas_dir} não existe.")
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
        print("Não foram encontradas notas em {notas_dir}.")

    # return filenames


if __name__ == "__main__":

    stamp_filenames()

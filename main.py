import sys
import os
import argparse

from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".heic", ".heif"}
HEIC_EXTENSIONS = {".heic", ".heif"}


def make_dir(fname):
    try:
        os.mkdir(f"{fname}")
        dup_folder = fname
    except FileExistsError:
        dup_folder = os.listdir(os.getcwd())
        dup_folder = [file for file in dup_folder if file.startswith(fname) and not '.' in file[len(fname):]]
        dup_folder = max(dup_folder)
        t = dup_folder[-1]
        if t.isnumeric():
            dup_folder = dup_folder[:-1] + str(int(t) + 1)
        else:
            dup_folder = dup_folder + "1"
        os.mkdir(dup_folder)
    return dup_folder

def pdf2img(pdf_file, no_dir):
    try:
        if not os.path.exists(pdf_file) or pdf_file[-4:]!=".pdf":
                raise FileNotFoundError(pdf_file)
        else:
            fname = pdf_file[:-4]
            dup_folder = ''
            if not no_dir:
                dup_folder = make_dir(fname)
                print("Converting Wait!!")
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_file)
            i = -1 # Initialize i to handle cases where the loop might not run
            for i, img in enumerate(images):
                if dup_folder:
                    img.save(f'{dup_folder}/{fname}{i+1}.jpg', 'JPEG')
                else:
                    img.save(f'{fname}{i+1}.jpg', 'JPEG')
    
            if not no_dir and dup_folder:
                print("", (i+1), ("image" if i == 1 else "images"), "saved in", dup_folder)
            else:
                print("", (i+1), ("image" if i == 1 else "images"), "saved in current working directory")
    except FileNotFoundError as e:
        print(f"File '{e.args[0]}' not found, operation terminated")
        # print(e.args)
    except Exception as ex:
        print(f"Error occurred: {ex}")

def pdfunlock(pdf_file, password):
    import pikepdf
    try:
        if not os.path.exists(pdf_file) or pdf_file[-4:]!=".pdf":
            raise FileNotFoundError(pdf_file)
        else:
            pdf = pikepdf.open(pdf_file, password=password)
            pdf.save(f"{pdf_file[:-4]}_unlocked.pdf")
            print("Pdf unlocked!!")
    except FileNotFoundError as e:
        print(f"File '{e.args[0]}' not found, operation terminated")
    except Exception as ex:
        print(f"Error occurred: {ex}")

def pdf2docx(pdf_file, no_dir):
    try:
        if not os.path.exists(pdf_file) or pdf_file[-4:] != ".pdf":
            raise FileNotFoundError(pdf_file)

        import pdf2docx

        output_file = f"{pdf_file[:-4]}.docx"
        converter = pdf2docx.Converter(pdf_file)
        converter.convert(output_file, start=0, end=None)
        converter.close()
        print(f"Converted DOCX saved as {output_file}")
    except ModuleNotFoundError:
        print("Error occurred: pdf2docx is not installed")
    except FileNotFoundError as e:
        print(f"File '{e.args[0]}' not found, operation terminated")
    except Exception as ex:
        print(f"Error occurred: {ex}")

def heic2jpg(output_dir, save_as_jpeg, *heic_files):
    try:
        if not heic_files:
            raise FileNotFoundError("No HEIC files provided")

        os.makedirs(output_dir, exist_ok=True)
        output_ext = ".jpeg" if save_as_jpeg else ".jpg"

        for heic_file in heic_files:
            ext = os.path.splitext(heic_file)[1].lower()
            if not os.path.exists(heic_file) or ext not in HEIC_EXTENSIONS:
                raise FileNotFoundError(heic_file)

            image = Image.open(heic_file).convert("RGB")
            output_file = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(heic_file))[0]}{output_ext}")
            image.save(output_file, "JPEG")
            print(f"Converted {heic_file} to {output_file}")
    except FileNotFoundError as e:
        print(f"File '{e.args[0]}' not found, operation terminated")
    except Exception as ex:
        print(f"Error occurred: {ex}")

def pdfmerge(output_file, *pdf_files):
    from PyPDF2 import PdfMerger
    merger = PdfMerger()
    try:
        for pdf in pdf_files:
            if not os.path.exists(pdf) or pdf[-4:]!=".pdf":
                raise FileNotFoundError(pdf)
            merger.append(pdf)
        if output_file[-4:]!=".pdf": output_file+=".pdf"
        merger.write(output_file)
        merger.close()
        print(f"Merged PDF saved as {output_file}")
    except FileNotFoundError as img_file_name:
        print(f"File '{img_file_name}' not found, operation terminated")
    except Exception as ex:
        print(f"Error occurred: {ex}")
        
        
def img2pdf(output_file, *img_files):
    # Convert images to PDF format
    img_formats = IMAGE_EXTENSIONS
    pdf_pages = []
    try:
        for img_file in img_files:
            if not os.path.exists(img_file) or os.path.splitext(img_file)[1].lower() not in img_formats:
                raise FileNotFoundError(img_file)
            img = Image.open(img_file).convert("RGB")  # Convert to RGB mode (required for PDF)
            pdf_pages.append(img)
        # Save the first image as PDF and append the rest
        if os.path.splitext(output_file)[1].lower() != ".pdf":
            output_file += ".pdf"
        pdf_pages[0].save(output_file, save_all=True, append_images=pdf_pages[1:])
        print(f"Converted PDF saved as {output_file}")
        
    except FileNotFoundError as e:
        print(f"File '{e.args[0]}' not found, operation terminated")
    except Exception as ex:
        print(f"Error occurred: {ex}")
        
def main():
    parser = argparse.ArgumentParser(description="Perform PDF operations")
    subparsers = parser.add_subparsers(dest="command")

    # PDF to Image
    parser_img = subparsers.add_parser("pdf2img",aliases=["p2i"], help="Convert PDF to images")
    parser_img.add_argument("pdf_file", help="PDF file to convert")
    parser_img.add_argument("-nodir", "--nodir", action="store_true", help="Save images in the current directory")
    
    # IMG convert
    parser_merge = subparsers.add_parser("img2pdf",aliases=["i2p"], help="Convert multiple IMGs to pdf")
    parser_merge.add_argument("output_file", help="Output merged PDF file")
    parser_merge.add_argument("img_files", nargs="+", help="IMG files to Convert")

    # HEIC convert
    parser_heic = subparsers.add_parser("heic2jpg", aliases=["h2j"], help="Convert HEIC images to JPG/JPEG")
    parser_heic.add_argument("heic_files", nargs="+", help="HEIC/HEIF files to convert")
    parser_heic.add_argument("-o", "--output-dir", default=os.getcwd(), help="Directory to save converted images")
    parser_heic.add_argument("--jpeg", action="store_true", help="Save output using the .jpeg extension")

    # PDF Unlock
    parser_unlock = subparsers.add_parser("unlock",aliases=["ul"], help="Unlock PDF file")
    parser_unlock.add_argument("pdf_file", help="PDF file to unlock")
    parser_unlock.add_argument("password", help="Password for the locked PDF")

    # PDF to DOCX
    parser_docx = subparsers.add_parser("pdf2docx", aliases=["p2d"], help="Convert PDF to DOCX")
    parser_docx.add_argument("pdf_file", help="PDF file to convert")

    # PDF Merge
    parser_merge = subparsers.add_parser("merge",aliases=["m"], help="Merge multiple PDFs")
    parser_merge.add_argument("output_file", help="Output merged PDF file")
    parser_merge.add_argument("pdf_files", nargs="+", help="PDF files to merge")
    
    args = parser.parse_args()

    if args.command in ["pdf2img","p2i"]:
        pdf2img(args.pdf_file, args.nodir)
    elif args.command in ["img2pdf","i2p"]:
        img2pdf(args.output_file, *args.img_files)
    elif args.command in ["heic2jpg", "h2j"]:
        heic2jpg(args.output_dir, args.jpeg, *args.heic_files)
    elif args.command in ["unlock","ul"]:
        pdfunlock(args.pdf_file, args.password)
    elif args.command in ["pdf2docx", "p2d"]:
        pdf2docx(args.pdf_file, False)
    elif args.command in ["merge","m"]:
        pdfmerge(args.output_file, *args.pdf_files)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

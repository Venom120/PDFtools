import os
import zipfile
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Toplevel, Listbox, Button, IntVar, Entry
from tkinter.ttk import *
from ttkthemes import ThemedTk
from PIL import Image
from PyPDF2 import PdfMerger
import pikepdf
from pdf2image import convert_from_path
from PyPDF2.errors import PdfReadError
from PyPDF2 import PdfReader

# Global Variables
def make_dir(fname, output_dir):
    folder_path = os.path.join(output_dir, fname)
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    return folder_path

def is_valid_pdf(file_path):
    try:
        reader = PdfReader(file_path)
        num_pages = len(reader.pages)
        return num_pages > 0
    except (PdfReadError, FileNotFoundError, Exception):
        return False

def select_file():
    if os.name == 'posix':
        result = os.popen('kdialog --getopenfilename').read().strip()
    else:
        result = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf"), ("Image files", "*.jpg;*.jpeg;*.png"), ("ZIP files", "*.zip")])
    return result

def select_multiple_files():
    if os.name == 'posix':
        result = os.popen('kdialog --getopenfilename --multiple --separate-output').read().strip().split('\n')
    else:
        result = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf"), ("Image files", "*.jpg;*.jpeg;*.png"), ("ZIP files", "*.zip")])
    return [f for f in result if f]

def select_folder():
    if os.name == 'posix':
        result = os.popen('kdialog --getexistingdirectory').read().strip()
    else:
        result = filedialog.askdirectory(title="Select Output Folder")
    return result

def reorder_files(files):
    def move_up():
        selected = lb.curselection()
        for i in selected:
            if i > 0:
                temp = files[i]
                files[i], files[i - 1] = files[i - 1], temp
                lb.delete(0, tk.END)
                for f in files:
                    lb.insert(tk.END, os.path.basename(f))
                lb.select_set(i - 1)

    def move_down():
        selected = lb.curselection()
        for i in selected:
            if i < len(files) - 1:
                temp = files[i]
                files[i], files[i + 1] = files[i + 1], temp
                lb.delete(0, tk.END)
                for f in files:
                    lb.insert(tk.END, os.path.basename(f))
                lb.select_set(i + 1)

    reorder_window = Toplevel(root)
    reorder_window.title("Reorder Files")
    lb = Listbox(reorder_window, selectmode=tk.SINGLE, height=10, width=50)
    lb.pack(pady=5)
    for f in files:
        lb.insert(tk.END, os.path.basename(f))
    Button(reorder_window, text="Move Up", command=move_up).pack(side=tk.LEFT, padx=5)
    Button(reorder_window, text="Move Down", command=move_down).pack(side=tk.RIGHT, padx=5)
    Button(reorder_window, text="Done", command=reorder_window.destroy).pack(pady=5)
    reorder_window.wait_window()
    return files

def create_input_window(task_func):
    def upload_file():
        nonlocal file_path
        if task_func in [pdfmerge, img2pdf]:
            file_path = select_multiple_files()
        else:
            file_path = select_file()
        if file_path:
            lbl_file.config(text=f"{len(file_path) if isinstance(file_path, list) else 1} file(s) selected")

    def select_output_folder():
        folder_selected = select_folder()
        if folder_selected:
            output_entry.delete(0, tk.END)
            output_entry.insert(0, folder_selected)

    def submit():
        if not file_path:
            messagebox.showerror("Error", "No file selected. Please upload a file.")
            return
        if not output_entry.get():
            messagebox.showerror("Error", "No output folder selected. Please choose an output location.")
            return
        task_func(file_path, chk_zip.get(), output_entry.get())
        messagebox.showinfo("Success", "Task completed successfully!")
        input_window.destroy()

    file_path = ""
    input_window = Toplevel(root)
    input_window.title("Upload and Configure")

    frame_top = tk.Frame(input_window)
    frame_top.pack(pady=5)
    Button(frame_top, text="Upload File(s)", command=upload_file).pack(side=tk.LEFT, padx=5)
    lbl_file = Label(frame_top, text="No file selected")
    lbl_file.pack(side=tk.LEFT, padx=5)

    chk_zip = IntVar()
    if task_func == pdf2img:
        Checkbutton(input_window, text="Save as ZIP", variable=chk_zip).pack(pady=5)

    Label(input_window, text="Output Folder Location:").pack(pady=5)
    output_frame = tk.Frame(input_window)
    output_frame.pack(pady=5)

    output_entry = Entry(output_frame, width=50)
    output_entry.pack(side=tk.LEFT, padx=(0, 5))
    Button(output_frame, text="Browse", command=select_output_folder).pack(side=tk.RIGHT)

    Button(input_window, text="Convert", command=submit).pack(pady=5)
    input_window.wait_window()

def pdf2img(file_path, zip_option, output_dir):
    if not is_valid_pdf(file_path):
        messagebox.showinfo("Error", f"Selected file is not a pdf")
        return
    if zip_option:
        temp_folder = os.path.join(output_dir, "temp_images")
        os.makedirs(temp_folder, exist_ok=True)
        images = convert_from_path(file_path)
        for i, img in enumerate(images):
            img.save(f'{temp_folder}/{os.path.basename(file_path)}_{i+1}.jpg', 'JPEG')
        zip_name = os.path.join(output_dir, f'{os.path.basename(file_path)[:-4]}.zip')
        shutil.make_archive(zip_name.replace('.zip', ''), 'zip', temp_folder)
        shutil.rmtree(temp_folder, ignore_errors=True)
        messagebox.showinfo("Success", f"Images saved as {zip_name}")
    else:
        images = convert_from_path(file_path)
        for i, img in enumerate(images):
            img.save(f'{output_dir}/{os.path.basename(file_path)}_{i+1}.jpg', 'JPEG')
        messagebox.showinfo("Success", "Images saved successfully!")

def pdfunlock(file_path, zip_option, output_dir):
    if not is_valid_pdf(file_path):
        messagebox.showinfo("Error", f"Selected file is not a pdf")
        return
    password = simpledialog.askstring("Password", "Enter PDF password:", show='*')
    try:
        with pikepdf.open(file_path, password=password) as pdf:
            output_file = os.path.join(output_dir, os.path.basename(file_path).replace('.pdf', '_unlocked.pdf'))
            pdf.save(output_file)
            messagebox.showinfo("Success", f"Unlocked PDF saved as {output_file}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to unlock PDF: {str(e)}")

def pdfmerge(file_path, zip_option, output_dir):
    if not file_path:
        messagebox.showerror("Error", "No files selected for merging.")
        return
    zip_folder = None
    if len(file_path) == 1 and file_path[0].endswith('.zip'):
        zip_folder = os.path.join(output_dir, "temp_merge")
        os.makedirs(zip_folder, exist_ok=True)
        with zipfile.ZipFile(file_path[0], 'r') as zip_ref:
            zip_ref.extractall(zip_folder)
        file_path = [os.path.join(zip_folder, f) for f in os.listdir(zip_folder) if f.endswith('.pdf')]
    order_files = reorder_files(file_path)
    merger = PdfMerger()
    for pdf in order_files:
        merger.append(pdf)
    output_file = os.path.join(output_dir, "merged.pdf")
    merger.write(output_file)
    merger.close()
    if zip_folder:
        shutil.rmtree(zip_folder, ignore_errors=True)
    messagebox.showinfo("Success", f"Merged PDF saved as {output_file}")

def img2pdf(file_path, zip_option, output_dir):
    zip_folder = None
    if len(file_path) == 1 and file_path[0].endswith('.zip'):
        zip_folder = os.path.join(output_dir, "temp_img")
        os.makedirs(zip_folder, exist_ok=True)
        with zipfile.ZipFile(file_path[0], 'r') as zip_ref:
            zip_ref.extractall(zip_folder)
        file_path = [os.path.join(zip_folder, f) for f in os.listdir(zip_folder) if f.lower().endswith(('jpg', 'jpeg', 'png'))]
    order_files = reorder_files(file_path)
    images = [Image.open(img).convert('RGB') for img in order_files]
    output_file = os.path.join(output_dir, "output.pdf")
    images[0].save(output_file, save_all=True, append_images=images[1:])
    if zip_folder:
        shutil.rmtree(zip_folder, ignore_errors=True)
    messagebox.showinfo("Success", f"PDF created as {output_file}")

# GUI Setup
root = ThemedTk(theme="breeze")
root.title("PDF Toolkit")
root.geometry("500x400")

Label(root, text="PDF Toolkit", font=("Helvetica", 16)).pack(pady=10)
Button(root, text="PDF to Image", command=lambda: create_input_window(pdf2img)).pack(pady=5)
Button(root, text="Unlock PDF", command=lambda: create_input_window(pdfunlock)).pack(pady=5)
Button(root, text="Merge PDFs", command=lambda: create_input_window(pdfmerge)).pack(pady=5)
Button(root, text="Images to PDF", command=lambda: create_input_window(img2pdf)).pack(pady=5)

root.mainloop()

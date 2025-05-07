# PDFtools
## windows app
Follow this [link](https://github.com/Venom120/PDFtools/releases/download/v1/pdftools.exe) to download the exe file!!
Windows defender may block it because i have disabled console windows

## console
First, run `Run_me_First.py` file (to add this folder to your environment variables).

Also, complete the process mentioned in this link:
[https://stackoverflow.com/a/53960829](https://stackoverflow.com/a/53960829)

Then, from anywhere, you can run:

### Convert PDF to Images
```
> pdf.bat pdf2img <pdf_file_name>
```
To save images in the same directory without creating a separate folder, use:
```
> pdf.bat pdf2img <pdf_file_name> --nodir
```

### Unlock a Locked PDF
```
> pdf.bat pdfunlock <pdf_file_name> <password>
```

### Merge Multiple PDFs
```
> pdf.bat pdfmerge <output_file_name> <pdf1> <pdf2> <pdf3> ...
```

This setup allows you to use `pdf.bat` from anywhere on your system to perform the required PDF operations.


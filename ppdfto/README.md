ppdfto — sample PDFs for testing

This folder contains a small script to generate sample PDF files for testing PDF loaders, splitters, and embedding workflows.

Files:
- generate_sample_pdfs.py — Python script that writes `sample1.pdf` and `sample2.pdf`.

Requirements:
- Python 3.8+
- reportlab (install in your project venv):

```powershell
& .\myenv\Scripts\Activate.ps1
pip install reportlab
```

Usage:

```powershell
& .\myenv\Scripts\python.exe .\ppdfto\generate_sample_pdfs.py
```

This will produce `sample1.pdf` and `sample2.pdf` in the `ppdfto` folder.

After generation you can load the PDFs in your notebook with `PyPDFLoader` or other loaders.

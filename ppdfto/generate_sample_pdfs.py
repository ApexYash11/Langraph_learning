"""Generate two simple sample PDF files for testing.
Requires: reportlab (pip install reportlab)

Usage:
    python generate_sample_pdfs.py
This will create `sample1.pdf` and `sample2.pdf` in the same folder.
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
from pathlib import Path

OUT_DIR = Path(__file__).parent


def make_pdf(path: Path, title: str, body: str):
    c = canvas.Canvas(str(path), pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 18)
    c.drawString(72, height - 72, title)
    c.setFont("Helvetica", 12)
    y = height - 110
    for line in body.splitlines():
        c.drawString(72, y, line)
        y -= 18
        if y < 72:
            c.showPage()
            y = height - 72
    c.showPage()
    c.save()


if __name__ == "__main__":
    now = datetime.utcnow().isoformat()
    p1 = OUT_DIR / "sample1.pdf"
    p2 = OUT_DIR / "sample2.pdf"

    body1 = f"Sample PDF 1\nGenerated: {now}\n\nThis is a small example PDF used for testing PDF loaders and vectorization.\n\nItems:\n- alpha\n- beta\n- gamma"
    body2 = f"Sample PDF 2\nGenerated: {now}\n\nAnother sample file. Use this to test multi-document ingestion.\n\nNotes:\n1) Test parsing\n2) Test splitting\n3) Test embedding"

    make_pdf(p1, "Sample PDF 1", body1)
    print(f"Wrote: {p1}")
    make_pdf(p2, "Sample PDF 2", body2)
    print(f"Wrote: {p2}")

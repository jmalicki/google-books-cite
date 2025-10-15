"""Integration tests for google-books-cite package."""

import subprocess
import tempfile
import shutil
from pathlib import Path
import json


def test_gbaux_generation():
    """Test that .gbaux file is generated with correct JSON."""
    # Create test document
    test_tex = r"""
\documentclass{article}
\usepackage{hyperref}
\usepackage{google-books-cite}
\usepackage[backend=biber]{biblatex}
\addbibresource{test.bib}
\begin{document}
\gbparencite[p.~312]{TestBook}
\gbparencite[pp.~45-67]{TestBook}
\end{document}
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Write test files
        (tmppath / "test.tex").write_text(test_tex)
        (tmppath / "test.bib").write_text("@book{TestBook, author={Author}, title={Title}, year={2000}}")
        
        # Copy package
        shutil.copy("google-books-cite.sty", tmppath / "google-books-cite.sty")
        
        # Compile
        result = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "test.tex"],
            cwd=tmppath,
            capture_output=True
        )
        
        # Check .gbaux was created
        gbaux_file = tmppath / "test.gbaux"
        assert gbaux_file.exists(), "gbaux file not created"
        
        # Parse JSON
        with open(gbaux_file) as f:
            data = json.load(f)
        
        # Verify content
        assert len(data) == 2, f"Expected 2 entries, got {len(data)}"
        assert data[0] == {"key": "TestBook", "page": "p.~312"}
        assert data[1] == {"key": "TestBook", "page": "pp.~45-67"}
        
        print("✓ .gbaux generation works correctly")


def test_link_generation():
    """Test that gbfind --make-links generates correct .gblinks.tex file."""
    from tools.gbfind.linkgen import generate_links_file
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Create test .gbaux
        gbaux_data = [
            {"key": "TestBook", "page": "p.~312"},
            {"key": "TestBook", "page": "pp.~45-67"},
            {"key": "NoID", "page": "p.~100"}
        ]
        gbaux_file = tmppath / "test.gbaux"
        with open(gbaux_file, 'w') as f:
            json.dump(gbaux_data, f)
        
        # Create test .bib with Google Books ID
        bib_content = """
@book{TestBook,
  author = {Test Author},
  title = {Test Title},
  year = {2000},
  googlebooksid = {ABC123xyz},
}

@book{NoID,
  author = {Other},
  title = {No ID},
  year = {2001},
}
"""
        bib_file = tmppath / "test.bib"
        bib_file.write_text(bib_content)
        
        # Generate links
        output_file = tmppath / "test.gblinks.tex"
        count = generate_links_file(str(gbaux_file), str(bib_file), str(output_file))
        
        # Verify
        assert count == 2, f"Expected 2 links, got {count}"
        assert output_file.exists(), "Output file not created"
        
        # Check content
        content = output_file.read_text()
        assert "gblink@TestBook@p.~312" in content
        assert "id=ABC123xyz&pg=PA312" in content
        assert "id=ABC123xyz&pg=PA45" in content  # First page of range
        assert "NoID" not in content  # Should not include entry without ID
        
        print("✓ Link generation works correctly")


def test_end_to_end_pdf_links():
    """
    End-to-end test: compile document, generate links, recompile, verify PDF.
    """
    test_tex = r"""
\documentclass{article}
\usepackage{hyperref}
\usepackage{google-books-cite}
\usepackage[backend=biber]{biblatex}
\addbibresource{test.bib}
\begin{document}
Citation: \gbparencite[p.~312]{TestBook}
\end{document}
"""
    
    test_bib = """
@book{TestBook,
  author = {Arthur Schopenhauer},
  title = {Test Title},
  year = {1969},
  googlebooksid = {NbsVAAAAYAAJ},
}
"""
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        
        # Write files
        (tmppath / "test.tex").write_text(test_tex)
        (tmppath / "test.bib").write_text(test_bib)
        shutil.copy("google-books-cite.sty", tmppath)
        
        # Pass 1: Generate .gbaux
        subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "test.tex"],
            cwd=tmppath,
            capture_output=True
        )
        
        assert (tmppath / "test.gbaux").exists(), "gbaux not created"
        
        # Generate links
        from tools.gbfind.linkgen import generate_links_file
        count = generate_links_file(
            str(tmppath / "test.gbaux"),
            str(tmppath / "test.bib"),
            str(tmppath / "test.gblinks.tex")
        )
        
        assert count == 1, f"Expected 1 link, got {count}"
        
        # Pass 2: Compile with links
        subprocess.run(
            ["xelatex", "-interaction=nonstopmode", "test.tex"],
            cwd=tmppath,
            capture_output=True
        )
        
        # Verify PDF
        pdf_file = tmppath / "test.pdf"
        assert pdf_file.exists(), "PDF not created"
        
        # Check PDF contains the Google Books URL
        pdf_bytes = pdf_file.read_bytes()
        assert b"books.google.com" in pdf_bytes, "Google Books URL not in PDF"
        assert b"NbsVAAAAYAAJ" in pdf_bytes, "Google Books ID not in PDF"
        assert b"pg=PA312" in pdf_bytes or b"pg=PA31" in pdf_bytes, "Page parameter not in PDF"
        
        print("✓ End-to-end test passed: PDF contains clickable Google Books links")


if __name__ == "__main__":
    print("Running google-books-cite integration tests...\n")
    
    test_gbaux_generation()
    test_link_generation()
    test_end_to_end_pdf_links()
    
    print("\n✅ All tests passed!")


#!/usr/bin/env python3
# Test 2: Does Python generate .gblinks.tex correctly?

import json
import sys
sys.path.insert(0, 'tools')

from gbfind.linkgen import generate_links_file

# Create test .gbaux
with open('test2.gbaux', 'w') as f:
    json.dump([
        {"key": "Book1", "page": "p.~312"},
        {"key": "Book2", "page": "pp.~45-67"}
    ], f)

# Create test .bib  
with open('test2.bib', 'w') as f:
    f.write("""
@book{Book1,
  title = {Test},
  googlebooksid = {ABC123},
}

@book{Book2,
  title = {Other},
  googlebooksid = {XYZ789},
}
""")

# Generate links
count = generate_links_file('test2.gbaux', 'test2.bib', 'test2.gblinks.tex')

print(f"✓ Test 2 PASS: Generated {count} links")
print("Contents of test2.gblinks.tex:")
with open('test2.gblinks.tex') as f:
    print(f.read())

# Verify URLs
with open('test2.gblinks.tex') as f:
    content = f.read()
    assert 'id=ABC123&pg=PA312' in content, "Missing Book1 URL"
    assert 'id=XYZ789&pg=PA45' in content, "Missing Book2 URL"
    print("✓ URLs contain correct IDs and page numbers")

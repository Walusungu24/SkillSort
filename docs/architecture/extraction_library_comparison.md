# CV Extraction Library Comparison

**Task:** S1-04 — Extraction library comparison
**Author:** Developer 2 — CV Processing & Information Extraction
**Date:** November 2026

## Purpose

Evaluate available Python libraries for extracting text from PDF and DOCX CV files.
This comparison documents the trade-offs, limitations, and recommendations that inform
the SkillsSort extraction pipeline.

---

## PDF Extraction Libraries

### 1. pdfplumber

| Aspect | Details |
|--------|---------|
| **Version tested** | 0.11.10 |
| **Underlying engine** | pdfminer.six |
| **Strengths** | Best-in-class for layout-aware extraction. Handles multi-column PDFs, tables, and grouped text better than alternatives. Can extract text with positional metadata (x0, y0, x1, y1). Also supports table extraction with `extract_tables()`. |
| **Weaknesses** | Slower than pypdf for simple text-only PDFs. Dependency chain includes pdfminer.six and pypdfium2. |
| **Best for** | CVs with complex layouts, multi-column designs, or table-formatted skills/education sections. |
| **Verdict** | **Primary PDF extractor.** Use this first for all PDF CVs. |

### 2. pypdf

| Aspect | Details |
|--------|---------|
| **Version tested** | 7.0.0 |
| **Underlying engine** | Pure Python (no C dependencies) |
| **Strengths** | Lightweight, fast, pure-Python (no system dependencies). Good for simple, text-based PDFs. Can also merge, split, encrypt/decrypt, and fill PDF forms. |
| **Weaknesses** | Layout fidelity is poor compared to pdfplumber. Multi-column or table-heavy PDFs may produce garbled or interleaved text. No table extraction support. |
| **Best for** | Simple single-column PDFs, or as a fallback when pdfplumber fails. |
| **Verdict** | **Fallback PDF extractor.** Use when pdfplumber returns empty text or errors. |

### 3. pypdfium2

| Aspect | Details |
|--------|---------|
| **Version tested** | 5.15.1 (installed as pdfplumber dependency) |
| **Underlying engine** | Google's PDFium (C++ library with Python bindings) |
| **Strengths** | Very fast rendering. Can render PDF pages as images (useful for OCR fallback on scanned PDFs). |
| **Weaknesses** | Text extraction is secondary; primarily a rendering library. No high-level text extraction API. |
| **Best for** | Rendering PDF pages to images for OCR processing of scanned CVs. |
| **Verdict** | **Future use** for scanned-document OCR pipeline. Not used in current POC. |

### 4. PyMuPDF (fitz) — Not tested but noted

| Aspect | Details |
|--------|---------|
| **Strengths** | Very fast, excellent text extraction quality. Supports text extraction with font info, images, and annotations. |
| **Weaknesses** | AGPL license (may require commercial license for proprietary use). Larger dependency. |
| **Verdict** | Worth evaluating if extraction speed becomes a bottleneck and license terms are acceptable. |

---

## DOCX Extraction Libraries

### 1. python-docx

| Aspect | Details |
|--------|---------|
| **Version tested** | 1.2.0 |
| **Strengths** | Direct access to paragraphs, runs, tables, styles, and document structure. Preserves document hierarchy (headings, bullet lists). Can also write/modify DOCX files (used for synthetic CV generation). |
| **Weaknesses** | Does not handle DOC (old binary format). Embedded objects (images, charts) are not text-extractable. |
| **Best for** | All DOCX CVs. This is the standard and only DOCX library needed. |
| **Verdict** | **Primary DOCX extractor.** No alternative needed at this stage. |

---

## Scanned PDFs and Image-Based Documents

Scanned CVs (photographed or scanned paper documents) produce PDFs with no extractable text.
Neither pdfplumber nor pypdf can extract text from these — they will return empty strings.

**Recommended approach for future implementation:**

1. Detect image-only PDFs (pdfplumber returns empty text but page has images)
2. Render PDF pages to images using `pypdfium2`
3. Pass images through an OCR engine:
   - **Tesseract** (via `pytesseract`): Open source, good accuracy for clean scans
   - **AWS Textract** / **Google Document AI**: Cloud services, better for messy scans and handwriting
4. Post-process OCR output with the same field extraction logic

**Trade-offs:**
- Tesseract: Free, local, but requires manual language pack installation. Accuracy drops with low-quality scans.
- Cloud OCR: Better accuracy, handles handwriting, but costs money and requires internet access + data privacy review.

---

## Extraction Strategy Summary

```
Input File
    │
    ├── .pdf ──→ pdfplumber ──→ (text?) ──→ YES → Field Extraction
    │                           │
    │                           └── NO → pypdf ──→ (text?) ──→ YES → Field Extraction
    │                                                   │
    │                                                   └── NO → Flag as "scanned/unsupported"
    │
    ├── .docx ──→ python-docx ──→ Field Extraction
    │
    └── other ──→ Flag as "unsupported format"
```

### Key Decisions

| Decision | Rationale |
|----------|----------|
| Use pdfplumber as primary PDF extractor | Best layout handling, handles tables and multi-column |
| Use pypdf as fallback | Catches cases where pdfplumber fails; pure Python, no system deps |
| Use python-docx for DOCX | Standard library, also used for synthetic CV generation |
| Defer OCR to future phase | Scanned CVs are not in the initial test set; add when stakeholder confirms frequency |
| Do not use PyMuPDF | License concerns (AGPL) for a team project |

---

## Performance Notes (from POC testing)

| Metric | Observation |
|--------|-----------|
| DOCX extraction speed | Near-instant (< 0.1s per file) |
| PDF extraction speed (pdfplumber) | ~0.5-2s per file depending on complexity |
| PDF extraction speed (pypdf) | < 0.5s per file |
| Accuracy (simple layout) | All fields extracted correctly for both PDF and DOCX |
| Accuracy (missing fields) | Correctly identifies absent fields and flags uncertain_fields |
| Accuracy (overlapping dates) | Detects overlaps and flags experience_years_estimate as uncertain |
| Consistency PDF vs DOCX | Results are identical between PDF and DOCX versions of the same synthetic CV |

---

## Limitations and Known Issues

1. **Scanned PDFs**: No text extraction possible without OCR (documented above)
2. **Password-protected PDFs**: Both libraries will error; the POC catches this and returns a "failed" status
3. **Gender marker (F/M)**: Not extracted — per roadmap, this must not influence ranking and requires stakeholder clarification
4. **Experience calculation with only years (no months)**: Uses January as start month and December as end month by default, producing slightly inflated estimates. Flagged as uncertain.
5. **Name extraction**: Relies on the name appearing as the first recognizable text. CVs that start with a photo or address block may fail.
6. **Non-English documents**: Regex patterns are designed for English-language CVs. Multi-language support would require additional patterns.

---

## Recommendations for Next Phase

1. **Add OCR support** after stakeholder confirms how common scanned CVs are
2. **Evaluate pdfplumber's table extraction** for CVs that use table-based layouts for skills/education
3. **Build a larger synthetic test set** with more layout variations (two-column designs, photo headers, non-standard fonts)
4. **Measure per-field accuracy** against a manually-labeled gold standard
5. **Consider spaCy or regex + NLP hybrid** for more robust name and institution extraction

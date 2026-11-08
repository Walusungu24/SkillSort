# Decision Log

This document records key technical and product decisions made by the SkillsSort
team. Each entry includes the date, the decision, the rationale, and who was
involved.

---

## DL-001: Use Django as the web framework

**Date:** October 2026
**Decision:** Use Django with Django templates for the initial MVP.
**Rationale:** All three developers are learning; Django provides batteries-included
features (admin, auth, ORM, forms) that reduce setup time. Templates are sufficient
for the MVP; a separate frontend can be added later if needed.
**Status:** Confirmed
**Participants:** All developers

---

## DL-002: Use SQLite for local development, PostgreSQL for production

**Date:** October 2026
**Decision:** SQLite for local development, PostgreSQL proposed for production.
**Rationale:** SQLite requires no setup and lets developers start immediately.
PostgreSQL is the proposed production database per the roadmap. Settings.py now
supports both via DATABASE_URL environment variable.
**Status:** Proposed (PostgreSQL pending team confirmation)
**Participants:** Developer 1

---

## DL-003: Shared data contract via ExtractionResult dataclass

**Date:** October 2026
**Decision:** Developer 2's extraction pipeline returns an `ExtractionResult`
dataclass defined in `apps/applicants/contracts.py`.
**Rationale:** Provides a single source of truth for the extraction output schema.
Developer 1's backend and Developer 3's frontend both consume this contract.
**Status:** Confirmed
**Participants:** Developer 1, Developer 2

---

## DL-004: Use pdfplumber as primary PDF extractor, pypdf as fallback

**Date:** November 2026
**Decision:** pdfplumber is the primary PDF text extraction library; pypdf is the
fallback when pdfplumber returns empty text or errors.
**Rationale:** pdfplumber handles multi-column layouts and tables better. pypdf is
lighter and catches edge cases. See `docs/architecture/extraction_library_comparison.md`
for the full comparison.
**Status:** Confirmed
**Participants:** Developer 2

---

## DL-005: Use python-docx for DOCX extraction

**Date:** November 2026
**Decision:** python-docx is the sole DOCX extraction library.
**Rationale:** Standard library for DOCX reading and writing. Also used for
synthetic CV generation. No alternative needed at this stage.
**Status:** Confirmed
**Participants:** Developer 2

---

## DL-006: OCR deferred to future phase

**Date:** November 2026
**Decision:** Scanned PDF/image-based document OCR is not included in the initial
POC or MVP.
**Rationale:** Scanned CVs are not in the initial test set. Adding OCR requires
additional dependencies (Tesseract or cloud services) and data privacy review.
Will be revisited after stakeholder confirms how common scanned CVs are.
**Status:** Deferred
**Participants:** Developer 2

---

## DL-007: One shared applicant model (not per-category tables)

**Date:** October 2026
**Decision:** Use a single applicant record structure across all job categories
rather than separate tables per worksheet tab.
**Rationale:** The stakeholder's Excel workbook has four tabs with similar but not
identical columns. A person may appear in multiple tabs. One shared model with
category/vacancy associations avoids duplicate records.
**Status:** Proposed (pending data model agreement)
**Participants:** Developer 1

---

## Open Questions (pending stakeholder confirmation)

These items from the roadmap require stakeholder input before a final decision:

1. What does the Rating (0-1) field represent?
2. How is experience-years calculated today?
3. What does "With Chinese" mean in the recruitment workflow?
4. What does "Interviewed" represent?
5. Should gender be included in the software at all?
6. One applicant profile with multiple associations, or separate records per application?
7. Which columns should appear in spreadsheet export?
8. Does every batch correspond to a specific job description?
9. How common are scanned/image-based CVs?
10. What is the acceptable review process for low-confidence extraction?
11. Who is authorized to access applicant records and how long should CVs be retained?
12. What counts as success for the first pilot?

See roadmap section 5 for full details.

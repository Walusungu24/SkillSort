# Requirements

This document captures the working requirements for SkillsSort. It is provisional
and will be updated as the stakeholder confirms ambiguous items.

## Current status

Requirements refinement phase. The stakeholder's Excel workbook has been reviewed
but some columns are ambiguous. Open questions are tracked in the decision log
(`docs/decisions/decision-log.md`).

## MVP scope (provisional)

1. **Batch upload** — Allow a recruiter to upload multiple supported CVs.
2. **Document text extraction** — Extract text from PDF and DOCX files.
3. **Field extraction** — Extract name, contact, education, qualification, work
   history, skills, certifications, and employment dates when available.
4. **Experience estimate** — Calculate estimated total duration when dates are
   clear. Show "unknown" or "needs review" when uncertain.
5. **Results table** — One applicant per row with sortable/searchable fields.
   Missing or uncertain values must be visible.
6. **Original CV link** — Access-controlled link to the source document.
7. **Category/vacancy association** — Associate results with a professional
   category and, if confirmed, a specific vacancy.
8. **Human review** — Recruiters can correct extracted fields. The software must
   not automatically reject applicants.
9. **Spreadsheet export** — CSV/XLSX export with confirmed column layout.
10. **Processing status** — Show success, partial extraction, and failure states.

## Known CV sources (from stakeholder)

- Job websites
- WhatsApp career groups
- Status posts

## Observed volumes (examples, not averages)

- Fewer than 10 for some posts
- Around 20 in some group posts
- Roughly 400 for widely advertised vacancies

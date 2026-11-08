# Roadmap

This is a condensed version of the team roadmap. For the full document, see the
shared SkillsSort Updated Development Roadmap.

## Phases

### Phase 0 — Repository and team setup
- [x] All developers have repository access
- [x] README, .gitignore, and docs directory
- [x] Branch and pull-request rules established
- [x] Environment variables for secrets; synthetic data for tests

### Phase 1 — Requirements and technical feasibility
- [x] Review Excel workbook; confirm ambiguous columns with stakeholder
- [ ] Map workbook fields to shared applicant schema (pending stakeholder answers)
- [x] Create synthetic CVs with varied layouts
- [x] Prototype PDF/DOCX text extraction; record accuracy and failure cases
- [ ] Sketch results table and export layout (Developer 3)

### Phase 2 — Agree the data contract and MVP
- [x] Agree field names, data types, optional fields, unknown representation
- [x] Define extraction input/output schema (contracts.py)
- [ ] Agree experience calculation rules and uncertainty display (drafted in docs)
- [ ] Confirm login, vacancy records, spreadsheet export, editable fields scope
- [ ] Write acceptance criteria before implementation of dependent features

### Phase 3 — First end-to-end vertical slice
- [ ] Upload one synthetic CV through the web interface
- [ ] Extract text and display clear success/failure result
- [ ] Show extracted fields; mark missing/uncertain values
- [ ] Protect original document from public access
- [ ] Add tests for valid document, invalid document, missing fields, failure

### Phase 4 — Batch workflow and applicant table
- [ ] Extend upload to multiple documents
- [ ] Display per-file status; allow partial batch success
- [ ] Persist records in PostgreSQL if confirmed in MVP
- [ ] Implement search, sorting, and secure CV link
- [ ] Add CSV/XLSX export

### Phase 5 — Quality and pilot
- [ ] Test varied CV layouts; calculate per-field accuracy
- [ ] Test duplicate detection, file limits, malformed files, permissions
- [ ] Measure processing time and manual correction time
- [ ] Demonstrate to stakeholder with synthetic or authorized data
- [ ] Prioritize feedback into next sprint

## Sprint 1 status

| Task | Owner | Status |
|------|-------|--------|
| S1-01 Repository collaboration | All | Done |
| S1-02 README and ignore rules | Dev 1 / Dev 2 | Done |
| S1-03 Django skeleton | Dev 1 / Dev 2 | Done |
| S1-04 Extraction library comparison | Dev 2 | Done |
| S1-05 Extraction proof of concept | Dev 2 | Done |
| S1-06 Results screen sketches | Dev 3 | Pending |
| S1-07 Synthetic test cases | Dev 2 + 3 | Done (Dev 2) |
| S1-08 Workbook questions and decision log | All / Dev 1 | Done (Dev 2) |

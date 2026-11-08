"""
Synthetic CV Generator for SkillsSort POC Testing
==================================================
Generates fake CV files (PDF and DOCX) with varied layouts, missing fields,
and different formatting to test the extraction pipeline.

IMPORTANT: All data is entirely fictional. No real applicant data is used.

Usage:
    python scripts/generate_synthetic_cvs.py

Output:
    tests/synthetic_cvs/*.pdf and *.docx files
"""

import os
from pathlib import Path

from docx import Document
from fpdf import FPDF

# ── Output directory ──────────────────────────────────────────────────────────
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "tests" / "synthetic_cvs"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ── Synthetic CV Data ─────────────────────────────────────────────────────────
CVS = [
    # ── CV 1: Well-structured, complete, clean format ──
    {
        "filename": "cv1_complete",
        "description": "Complete CV with all fields present, clean layout",
        "name": "Jane Mwangi",
        "phone": "+254 712 345 678",
        "email": "jane.mwangi@email.com",
        "institution": "University of Nairobi",
        "qualification": "Bachelor of Science in Computer Science",
        "experience": [
            "Software Developer, TechCorp Ltd, Jan 2021 – Dec 2023 (3 years)",
            "Junior Developer, StartUp Inc, Jun 2019 – Dec 2020 (1.5 years)",
        ],
        "skills": ["Python", "Django", "JavaScript", "PostgreSQL", "Docker", "Git"],
        "certifications": ["AWS Certified Developer Associate", "Scrum Master (CSM)"],
    },
    # ── CV 2: Missing some fields (no phone, no certifications) ──
    {
        "filename": "cv2_missing_fields",
        "description": "Missing phone and certifications, email-only contact",
        "name": "David Ochieng",
        "phone": None,
        "email": "d.ochieng@webmail.co.ke",
        "institution": "Kenyatta University",
        "qualification": "Bachelor of Commerce (Finance)",
        "experience": [
            "Accounts Assistant, ABC Ltd, Mar 2020 – Present (4 years)",
        ],
        "skills": ["Excel", "QuickBooks", "Financial Analysis", "Tax Preparation"],
        "certifications": [],
    },
    # ── CV 3: Overlapping experience dates ──
    {
        "filename": "cv3_overlapping_dates",
        "description": "Overlapping employment dates to test experience calculation",
        "name": "Sarah Kamau",
        "phone": "0722 987 654",
        "email": "sarah.k@careers.org",
        "institution": "Strathmore University",
        "qualification": "Bachelor of Business Administration (Human Resource)",
        "experience": [
            "HR Assistant, Global Services, Feb 2022 – Aug 2023 (1.5 years)",
            "Recruitment Intern, TalentHub, Jan 2022 – Jun 2022 (0.5 years, overlaps)",
            "HR Officer, PeopleFirst, Sep 2023 – Present (1 year)",
        ],
        "skills": ["Recruitment", "Onboarding", "HRIS", "Employee Relations"],
        "certifications": ["CIPD Level 5"],
    },
    # ── CV 4: Minimal info — name and email only ──
    {
        "filename": "cv4_minimal",
        "description": "Minimal CV — only name and email, everything else missing",
        "name": "Brian Otieno",
        "phone": None,
        "email": "brian.o@quickmail.com",
        "institution": None,
        "qualification": None,
        "experience": [],
        "skills": [],
        "certifications": [],
    },
    # ── CV 5: Different layout, abbreviations, no clear section headers ──
    {
        "filename": "cv5_unstructured",
        "description": "Unstructured CV — no clear section headers, abbreviations",
        "name": "Grace Wanjiru",
        "phone": "+254733456123",
        "email": "grace.wanjiru@gmail.com",
        "institution": "Moi University",
        "qualification": "BSc. Information Technology",
        "experience": [
            "IT Support Officer, DataSys, 2019 - 2021",
            "Systems Administrator, NetCore, 2021 - now",
        ],
        "skills": ["Networking", "Linux", "Windows Server", "SQL", "Python", "Bash"],
        "certifications": ["CCNA", "CompTIA Security+"],
    },
    # ── CV 6: Rich experience with many roles ──
    {
        "filename": "cv6_rich_experience",
        "description": "Many roles with clear dates, large skills list",
        "name": "Peter Njoroge",
        "phone": "+254 700 111 222",
        "email": "p.njoroge@professional.net",
        "institution": "Technical University of Kenya",
        "qualification": "Master of Science in Data Science",
        "experience": [
            "Data Scientist, AI Labs, Jan 2023 – Present (1.5 years)",
            "Data Analyst, Insight Analytics, Mar 2021 – Dec 2022 (1.75 years)",
            "Research Assistant, TUK, Sep 2019 – Feb 2021 (1.5 years)",
            "Teaching Assistant, TUK, Jan 2018 – Jun 2019 (1.5 years)",
        ],
        "skills": [
            "Python", "R", "SQL", "TensorFlow", "PyTorch", "Pandas",
            "Scikit-learn", "Tableau", "Power BI", "Spark", "AWS", "GCP",
        ],
        "certifications": [
            "Google Data Analytics Professional",
            "Microsoft Azure AI Engineer Associate",
        ],
    },
]


# ── DOCX Generation ───────────────────────────────────────────────────────────
def generate_docx(cv: dict, filepath: Path):
    """Generate a .docx CV file from synthetic data."""
    doc = Document()

    # Name as heading
    doc.add_heading(cv["name"], level=0)

    # Contact info
    contact_parts = []
    if cv["phone"]:
        contact_parts.append(f"Phone: {cv['phone']}")
    if cv["email"]:
        contact_parts.append(f"Email: {cv['email']}")
    if contact_parts:
        doc.add_paragraph(" | ".join(contact_parts))

    # Education
    if cv["institution"] or cv["qualification"]:
        doc.add_heading("Education", level=1)
        if cv["institution"]:
            doc.add_paragraph(f"Institution: {cv['institution']}")
        if cv["qualification"]:
            doc.add_paragraph(f"Qualification: {cv['qualification']}")

    # Experience
    if cv["experience"]:
        doc.add_heading("Work Experience", level=1)
        for exp in cv["experience"]:
            doc.add_paragraph(exp, style="List Bullet")

    # Skills
    if cv["skills"]:
        doc.add_heading("Skills", level=1)
        doc.add_paragraph(", ".join(cv["skills"]))

    # Certifications
    if cv["certifications"]:
        doc.add_heading("Certifications", level=1)
        for cert in cv["certifications"]:
            doc.add_paragraph(cert, style="List Bullet")

    doc.save(str(filepath))


# ── PDF Generation ────────────────────────────────────────────────────────────
def _ascii_safe(text: str) -> str:
    """Replace non-ASCII characters (like en-dashes) with ASCII equivalents."""
    replacements = {
        "\u2013": "-",  # en-dash
        "\u2014": "-",  # em-dash
        "\u2018": "'",  # left single quote
        "\u2019": "'",  # right single quote
        "\u201c": '"',  # left double quote
        "\u201d": '"',  # right double quote
        "\u2026": "...",  # ellipsis
    }
    for unicode_char, ascii_char in replacements.items():
        text = text.replace(unicode_char, ascii_char)
    return text.encode("ascii", errors="ignore").decode("ascii")


def generate_pdf(cv: dict, filepath: Path):
    """Generate a .pdf CV file from synthetic data using fpdf2."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Name
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, _ascii_safe(cv["name"]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    # Contact info
    pdf.set_font("Helvetica", "", 11)
    contact_parts = []
    if cv["phone"]:
        contact_parts.append(f"Phone: {_ascii_safe(cv['phone'])}")
    if cv["email"]:
        contact_parts.append(f"Email: {_ascii_safe(cv['email'])}")
    if contact_parts:
        pdf.cell(0, 7, " | ".join(contact_parts), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    # Education
    if cv["institution"] or cv["qualification"]:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Education", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        if cv["institution"]:
            pdf.cell(0, 6, f"Institution: {_ascii_safe(cv['institution'])}", new_x="LMARGIN", new_y="NEXT")
        if cv["qualification"]:
            pdf.cell(0, 6, f"Qualification: {_ascii_safe(cv['qualification'])}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # Experience
    if cv["experience"]:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Work Experience", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        for exp in cv["experience"]:
            pdf.cell(0, 6, _ascii_safe(f"  - {exp}"), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # Skills
    if cv["skills"]:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Skills", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 6, _ascii_safe(", ".join(cv["skills"])), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

    # Certifications
    if cv["certifications"]:
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "Certifications", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        for cert in cv["certifications"]:
            pdf.cell(0, 6, _ascii_safe(f"  - {cert}"), new_x="LMARGIN", new_y="NEXT")

    pdf.output(str(filepath))


# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("Generating synthetic CVs...\n")

    for cv in CVS:
        docx_path = OUTPUT_DIR / f"{cv['filename']}.docx"
        pdf_path = OUTPUT_DIR / f"{cv['filename']}.pdf"

        generate_docx(cv, docx_path)
        generate_pdf(cv, pdf_path)

        print(f"  ✓ {cv['filename']}.docx — {cv['description']}")
        print(f"  ✓ {cv['filename']}.pdf  — {cv['description']}")

    # Generate a deliberately invalid file for failure testing
    invalid_path = OUTPUT_DIR / "cv7_corrupt.txt"
    invalid_path.write_text("This is not a valid PDF or DOCX file.")
    print(f"\n  ✓ cv7_corrupt.txt — Invalid format for failure testing")

    print(f"\nDone! {len(CVS) * 2 + 1} files generated in {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

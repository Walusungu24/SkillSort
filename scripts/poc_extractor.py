"""
SkillsSort — CV Extraction Proof-of-Concept
=============================================
Standalone script that reads PDF and DOCX CV files and extracts structured
data conforming to the ExtractionResult data contract defined in
apps/applicants/contracts.py.

Usage:
    python scripts/poc_extractor.py                          # process all synthetic CVs
    python scripts/poc_extractor.py tests/synthetic_cvs/cv1_complete.pdf
    python scripts/poc_extractor.py tests/synthetic_cvs/cv1_complete.docx cv2_missing_fields.pdf

Author: Developer 2 — CV Processing & Information Extraction
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

# ── Ensure project root is importable ─────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from apps.applicants.contracts import ExtractionResult

# ── File type imports (lazy-loaded inside functions to handle import errors) ──


# ═══════════════════════════════════════════════════════════════════════════════
# TEXT EXTRACTION LAYER
# ═══════════════════════════════════════════════════════════════════════════════

def extract_text_from_pdf(filepath: Path) -> Tuple[str, str]:
    """
    Extract text from a PDF file.
    Tries pdfplumber first (better layout handling), falls back to pypdf.

    Returns:
        Tuple of (extracted_text, method_used)
    """
    errors = []

    # Attempt 1: pdfplumber (handles multi-column and table layouts better)
    try:
        import pdfplumber

        text_parts = []
        with pdfplumber.open(str(filepath)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
        text = "\n".join(text_parts).strip()
        if text:
            return text, "pdfplumber"
    except Exception as e:
        errors.append(f"pdfplumber: {e}")

    # Attempt 2: pypdf (lighter, sometimes works where pdfplumber fails)
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(filepath))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
        text = "\n".join(text_parts).strip()
        if text:
            return text, "pypdf"
    except Exception as e:
        errors.append(f"pypdf: {e}")

    # Both methods failed or produced no text
    error_detail = "; ".join(errors) if errors else "No text extracted"
    return "", error_detail


def extract_text_from_docx(filepath: Path) -> Tuple[str, str]:
    """
    Extract text from a DOCX file using python-docx.

    Returns:
        Tuple of (extracted_text, method_used)
    """
    try:
        from docx import Document

        doc = Document(str(filepath))
        text_parts = []

        # Extract paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)

        # Extract table content if present
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    text_parts.append(row_text)

        text = "\n".join(text_parts).strip()
        return text, "python-docx"
    except Exception as e:
        return "", f"python-docx: {e}"


def extract_text(filepath: Path) -> Tuple[str, str, Optional[str]]:
    """
    Extract text from a file based on its extension.

    Returns:
        Tuple of (text, method_used, error_message)
        If extraction fails, text will be empty and error_message will be set.
    """
    suffix = filepath.suffix.lower()

    if suffix == ".pdf":
        text, info = extract_text_from_pdf(filepath)
        if text:
            return text, info, None
        return "", "", f"PDF extraction failed: {info}"

    elif suffix == ".docx":
        text, info = extract_text_from_docx(filepath)
        if text:
            return text, info, None
        return "", "", f"DOCX extraction failed: {info}"

    else:
        return "", "", f"Unsupported file type: '{suffix}'. Supported: .pdf, .docx"


# ═══════════════════════════════════════════════════════════════════════════════
# FIELD EXTRACTION LAYER
# ═══════════════════════════════════════════════════════════════════════════════

# ── Email ─────────────────────────────────────────────────────────────────────
EMAIL_REGEX = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
)


def extract_email(text: str) -> Tuple[Optional[str], bool]:
    """Extract the first email address found. Returns (email, is_uncertain)."""
    match = EMAIL_REGEX.search(text)
    if match:
        return match.group(0), False
    return None, True


# ── Phone Number ──────────────────────────────────────────────────────────────
# Matches Kenyan and international phone formats:
# +254 712 345 678, 0712 345 678, +254733456123, 0722987654
PHONE_REGEX = re.compile(
    r"(?:\+?254[\s-]?)?"           # optional country code
    r"(?:0)?"                       # optional leading zero
    r"(7\d{2})"                     # first 3 digits (Kenyan mobile starts with 7)
    r"[\s.-]?"                      # optional separator
    r"(\d{3})"                      # next 3 digits
    r"[\s.-]?"                      # optional separator
    r"(\d{3})"                      # last 3 digits
)

# Broader fallback for non-Kenyan numbers
PHONE_FALLBACK_REGEX = re.compile(
    r"\+?\d{1,3}[\s.-]?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}"
)


def extract_phone(text: str) -> Tuple[Optional[str], bool]:
    """
    Extract a phone number from text.
    Returns (phone, is_uncertain).
    """
    # Try Kenyan format first
    match = PHONE_REGEX.search(text)
    if match:
        # Normalize: combine groups
        digits = "".join(match.groups())
        normalized = f"+254 {digits[:3]} {digits[3:6]} {digits[6:]}"
        return normalized, False

    # Try broader fallback
    match = PHONE_FALLBACK_REGEX.search(text)
    if match:
        return match.group(0).strip(), True  # uncertain because format is ambiguous

    return None, True


# ── Full Name ─────────────────────────────────────────────────────────────────
# Strategy: Take the first non-empty line that doesn't look like a header or label
HEADER_KEYWORDS = {
    "curriculum vitae", "resume", "cv", "profile",
    "education", "experience", "work experience", "skills",
    "certifications", "contact", "about", "summary",
    "professional", "employment", "qualifications",
}


def extract_name(text: str) -> Tuple[Optional[str], bool]:
    """
    Extract the candidate's full name.
    Strategy: first line that looks like a name (2+ capitalized words, not a header).

    Returns (name, is_uncertain).
    """
    lines = text.strip().split("\n")

    for line in lines[:15]:  # check first 15 lines
        line = line.strip()
        if not line or len(line) > 60:
            continue

        # Skip if it looks like a section header
        if line.lower() in HEADER_KEYWORDS:
            continue

        # Skip lines with email/phone/special chars
        if "@" in line or any(c.isdigit() for c in line):
            continue

        # Check if it looks like a name (2-4 words, mostly alphabetic)
        words = line.split()
        if 2 <= len(words) <= 4:
            if all(re.match(r"^[A-Za-z][A-Za-z.\-']*$", w) for w in words):
                return line, False

        # Single capitalized word (less confident)
        if len(words) == 1 and re.match(r"^[A-Z][a-z]+$", words[0]):
            return line, True

    # Fallback: look for "Name:" label
    name_match = re.search(r"(?:Name|NAME)\s*[:\-]\s*([A-Za-z\s]+)", text)
    if name_match:
        name = name_match.group(1).strip()
        if name:
            return name, False

    return None, True


# ── Institution ────────────────────────────────────────────────────────────────
INSTITUTION_KEYWORDS = re.compile(
    r"\b("
    r"University|College|Institute|Polytechnic|School of|Academy"
    r"|School"
    r")\b",
    re.IGNORECASE,
)


def extract_institution(text: str) -> Tuple[Optional[str], bool]:
    """
    Extract the primary educational institution.
    Returns (institution, is_uncertain).
    """
    # Look for institution keywords and capture surrounding context
    lines = text.split("\n")

    for line in lines:
        if INSTITUTION_KEYWORDS.search(line):
            # Clean up common label prefixes
            cleaned = re.sub(r"^(Institution|Education|School)\s*[:\-]\s*", "", line, flags=re.IGNORECASE).strip()
            # Take the portion containing the keyword
            match = INSTITUTION_KEYWORDS.search(cleaned)
            if match:
                # Get the full name around the keyword
                start = max(0, cleaned.rfind(",", 0, match.start()) + 1)
                end = cleaned.find(",", match.end())
                if end == -1:
                    end = len(cleaned)
                institution = cleaned[start:end].strip()
                # Clean trailing/leading separators
                institution = institution.strip(" |-:")
                if institution and len(institution) > 3:
                    return institution, False

    return None, True


# ── Qualification / Major ─────────────────────────────────────────────────────
QUALIFICATION_KEYWORDS = re.compile(
    r"\b("
    r"Bachelor(?:\s+of)?|BSc|B\.Sc|Master(?:\s+of)?|MSc|M\.Sc|MBA"
    r"|Diploma|Certificate|Degree|PhD|Ph\.D|Doctorate"
    r"|Associate|Higher (?:Diploma|Certificate)"
    r")\b",
    re.IGNORECASE,
)


def extract_qualification(text: str) -> Tuple[Optional[str], bool]:
    """
    Extract the qualification or field of study.
    Returns (qualification, is_uncertain).
    """
    lines = text.split("\n")

    for line in lines:
        if QUALIFICATION_KEYWORDS.search(line):
            cleaned = re.sub(
                r"^(Qualification|Education|Degree|Major|Field)\s*[:\-]\s*",
                "",
                line,
                flags=re.IGNORECASE,
            ).strip()
            # Truncate at reasonable length
            if len(cleaned) > 100:
                cleaned = cleaned[:100].rsplit(" ", 1)[0]
            if cleaned and len(cleaned) > 3:
                return cleaned, False

    return None, True


# ── Experience Years Estimate ────────────────────────────────────────────────
# Date patterns: "Jan 2021", "January 2021", "2021", "Jan 2021 – Dec 2023"
MONTH_PATTERN = r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"

DATE_RANGE_REGEX = re.compile(
    rf"({MONTH_PATTERN}?\s*)?"
    rf"(\d{{4}})"                           # start year
    rf"\s*[\-–]\s*"                        # separator (hyphen or en-dash)
    rf"({MONTH_PATTERN}?\s*)?"
    rf"(present|now|current|(\d{{4}}))",   # end year or "present"
    re.IGNORECASE,
)

YEAR_ONLY_REGEX = re.compile(
    r"(\d{4})\s*[\-–]\s*(present|now|current|(\d{4}))",
    re.IGNORECASE,
)


def calculate_experience_years(text: str) -> Tuple[Optional[float], bool, bool]:
    """
    Calculate estimated total years of experience from date ranges in text.

    Returns:
        (years, is_uncertain, has_overlap)
    """
    from datetime import datetime

    current_year = datetime.now().year
    durations = []  # list of (start_year, end_year, has_overlap_flag)
    has_any_overlap = False

    # Find all date ranges
    for match in DATE_RANGE_REGEX.finditer(text):
        start_year_str = match.group(2)
        start_month = match.group(1)
        end_part = match.group(4) or match.group(5)

        try:
            start_year = int(start_year_str)
            if end_part and end_part.lower() in ("present", "now", "current"):
                end_year = current_year
            elif end_part and end_part.isdigit():
                end_year = int(end_part)
            else:
                continue

            if end_year < start_year:
                continue

            # Approximate months from month names
            start_month_num = _month_to_num(start_month) if start_month else 1
            end_month_num = _month_to_num(match.group(3)) if match.group(3) else 12

            # Calculate duration in years (fractional)
            duration = (end_year - start_year) + (end_month_num - start_month_num) / 12.0
            duration = round(max(duration, 0), 2)
            durations.append((start_year, end_year, duration))

        except (ValueError, IndexError):
            continue

    # Also try year-only ranges (e.g., "2019 - 2021")
    # These are already handled by DATE_RANGE_REGEX since MONTH_PATTERN is optional,
    # so we skip this to avoid double-counting.

    if not durations:
        return None, True, False

    # Check for overlaps
    for i in range(len(durations)):
        for j in range(i + 1, len(durations)):
            s1, e1, _ = durations[i]
            s2, e2, _ = durations[j]
            if s1 <= e2 and s2 <= e1:
                has_any_overlap = True
                break

    # Sum durations (if overlaps, the total may be inflated)
    total_years = round(sum(d[2] for d in durations), 2)

    is_uncertain = has_any_overlap or len(durations) == 0
    return total_years, is_uncertain, has_any_overlap


def _month_to_num(month_str: Optional[str]) -> int:
    """Convert a month abbreviation or name to a number 1-12. Defaults to 1."""
    if not month_str:
        return 1
    month_str = month_str.strip()[:3].lower()
    months = {
        "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
        "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    }
    return months.get(month_str, 1)


# ── Skills ────────────────────────────────────────────────────────────────────
SKILL_SECTION_REGEX = re.compile(
    r"(?:Skills|Technical Skills|Core Competencies|Key Skills)\s*[:\n]",
    re.IGNORECASE,
)

# Common skill keywords to look for in text
COMMON_SKILLS = [
    "Python", "JavaScript", "TypeScript", "Java", "C++", "C#",
    "Django", "Flask", "FastAPI", "React", "Vue", "Angular",
    "Node.js", "PostgreSQL", "MySQL", "MongoDB", "SQLite", "Redis",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure",
    "Git", "Linux", "Bash", "PowerShell",
    "HTML", "CSS", "SQL", "NoSQL",
    "Excel", "PowerPoint", "Word",
    "QuickBooks", "SAP", "Oracle",
    "Networking", "Windows Server", "Active Directory",
    "TensorFlow", "PyTorch", "Pandas", "Scikit-learn", "NumPy",
    "Tableau", "Power BI", "Spark",
    "Financial Analysis", "Tax Preparation",
    "Recruitment", "Onboarding", "HRIS", "Employee Relations",
    "CCNA", "CompTIA", "ITIL",
    "R", "Scala", "Go", "Rust",
    "Jenkins", "CI/CD", "Terraform", "Ansible",
]


def extract_skills(text: str) -> Tuple[List[str], bool]:
    """
    Extract skills from text. Looks for a skills section first,
    then falls back to scanning for known skill keywords.

    Returns (skills_list, is_uncertain).
    """
    skills = []
    is_uncertain = False

    # Strategy 1: Find a "Skills" section and extract comma-separated items
    skill_section_match = SKILL_SECTION_REGEX.search(text)
    if skill_section_match:
        # Get text after the skills header until the next section or end
        start = skill_section_match.end()
        remaining = text[start:]

        # Find the next section header
        next_section = re.search(
            r"\n\s*(?:Education|Experience|Work|Certification|Contact|Summary|Profile|About)",
            remaining,
            re.IGNORECASE,
        )
        if next_section:
            skills_text = remaining[: next_section.start()]
        else:
            skills_text = remaining[:500]  # take first 500 chars

        # Parse comma-separated or newline-separated skills
        raw_skills = re.split(r"[,\n]", skills_text)
        for s in raw_skills:
            s = s.strip(" \t•-\n|")
            if s and len(s) > 1 and len(s) < 50:
                # Avoid duplicates
                if s not in skills:
                    skills.append(s)

    # Strategy 2: Scan for known skills if section extraction found few
    if len(skills) < 2:
        for skill in COMMON_SKILLS:
            pattern = re.compile(r"\b" + re.escape(skill) + r"\b", re.IGNORECASE)
            if pattern.search(text):
                # Use the canonical case from our list
                if skill not in skills:
                    skills.append(skill)

    if not skills:
        return [], True

    if len(skills) < 2:
        is_uncertain = True

    return skills, is_uncertain


# ── Certifications ───────────────────────────────────────────────────────────
CERT_SECTION_REGEX = re.compile(
    r"(?:Certifications?|Licenses?|Professional Development)\s*[:\n]",
    re.IGNORECASE,
)

CERT_KEYWORDS = [
    "AWS Certified", "Azure", "Google Cloud", "GCP",
    "Scrum Master", "CSM", "PMP", "PRINCE2",
    "CIPD", "CCNA", "CompTIA", "ITIL",
    "Microsoft Certified", "Oracle Certified",
    "CISSP", "CEH", "CISA",
]


def extract_certifications(text: str) -> Tuple[List[str], bool]:
    """
    Extract certifications from text.
    Returns (certifications_list, is_uncertain).
    """
    certs = []

    # Strategy 1: Find a certifications section
    cert_section_match = CERT_SECTION_REGEX.search(text)
    if cert_section_match:
        start = cert_section_match.end()
        remaining = text[start:]

        # Find next section
        next_section = re.search(
            r"\n\s*(?:Education|Experience|Work|Skills|Contact|Summary|Profile|About)",
            remaining,
            re.IGNORECASE,
        )
        if next_section:
            cert_text = remaining[: next_section.start()]
        else:
            cert_text = remaining[:500]

        raw_certs = re.split(r"[,\n]", cert_text)
        for c in raw_certs:
            c = c.strip(" \t•-\n|")
            if c and len(c) > 3 and len(c) < 80:
                if c not in certs:
                    certs.append(c)

    # Strategy 2: Scan for known certification keywords
    for cert in CERT_KEYWORDS:
        pattern = re.compile(re.escape(cert), re.IGNORECASE)
        if pattern.search(text):
            # Check we're not adding a substring of an existing cert
            already = any(cert.lower() in existing.lower() for existing in certs)
            if not already:
                certs.append(cert)

    return certs, len(certs) == 0


# ═══════════════════════════════════════════════════════════════════════════════
# MAIN EXTRACTION ORCHESTRATOR
# ═══════════════════════════════════════════════════════════════════════════════

def extract_from_file(filepath: Path) -> ExtractionResult:
    """
    Extract structured data from a single CV file.
    Returns an ExtractionResult conforming to the data contract.
    """
    filepath = Path(filepath)

    # Validate file exists
    if not filepath.exists():
        return ExtractionResult(
            raw_text="",
            parsing_status="failed",
            error_message=f"File not found: {filepath}",
        )

    # Validate file type
    suffix = filepath.suffix.lower()
    if suffix not in (".pdf", ".docx"):
        return ExtractionResult(
            raw_text="",
            parsing_status="failed",
            error_message=f"Unsupported file type: '{suffix}'. Supported: .pdf, .docx",
        )

    # Extract raw text
    raw_text, method, error = extract_text(filepath)

    if error or not raw_text:
        return ExtractionResult(
            raw_text=raw_text,
            parsing_status="failed",
            error_message=error or "No text could be extracted from the document.",
        )

    # ── Field-by-field extraction ────────────────────────────────────────────
    uncertain_fields = []

    # Name
    name, name_uncertain = extract_name(raw_text)
    if name_uncertain and name:
        uncertain_fields.append("full_name")

    # Email
    email, email_uncertain = extract_email(raw_text)
    if email_uncertain:
        uncertain_fields.append("email")

    # Phone
    phone, phone_uncertain = extract_phone(raw_text)
    if phone_uncertain:
        uncertain_fields.append("phone_number")

    # Institution
    institution, inst_uncertain = extract_institution(raw_text)
    if inst_uncertain:
        uncertain_fields.append("institution")

    # Qualification
    qualification, qual_uncertain = extract_qualification(raw_text)
    if qual_uncertain:
        uncertain_fields.append("qualification_major")

    # Experience years
    exp_years, exp_uncertain, exp_overlap = calculate_experience_years(raw_text)
    if exp_uncertain:
        uncertain_fields.append("experience_years_estimate")

    # Skills
    skills, skills_uncertain = extract_skills(raw_text)
    if skills_uncertain:
        uncertain_fields.append("skills")

    # Certifications
    certs, certs_uncertain = extract_certifications(raw_text)
    # Certs being empty is common, not necessarily uncertain
    # Only flag if there's a certification section we couldn't parse

    # ── Determine parsing status ─────────────────────────────────────────────
    extracted_count = sum(1 for v in [name, email, phone, institution, qualification, exp_years] if v is not None)
    extracted_count += 1 if skills else 0
    extracted_count += 1 if certs else 0

    if extracted_count >= 5:
        parsing_status = "success"
    elif extracted_count >= 2:
        parsing_status = "partial"
    else:
        parsing_status = "partial"

    return ExtractionResult(
        full_name=name,
        phone_number=phone,
        email=email,
        institution=institution,
        qualification_major=qualification,
        experience_years_estimate=exp_years,
        skills=skills,
        certifications=certs,
        raw_text=raw_text,
        parsing_status=parsing_status,
        uncertain_fields=uncertain_fields,
        error_message=None,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# CLI INTERFACE & REPORTING
# ═══════════════════════════════════════════════════════════════════════════════

def format_result(filepath: Path, result: ExtractionResult) -> str:
    """Format an ExtractionResult for readable terminal output."""
    lines = []
    lines.append("=" * 70)
    lines.append(f"  FILE: {filepath.name}")
    lines.append(f"  STATUS: {result.parsing_status.upper()}")
    if result.error_message:
        lines.append(f"  ERROR: {result.error_message}")
    if result.uncertain_fields:
        lines.append(f"  UNCERTAIN: {', '.join(result.uncertain_fields)}")
    lines.append("-" * 70)
    lines.append(f"  Name:           {result.full_name or '(not found)'}")
    lines.append(f"  Phone:          {result.phone_number or '(not found)'}")
    lines.append(f"  Email:          {result.email or '(not found)'}")
    lines.append(f"  Institution:    {result.institution or '(not found)'}")
    lines.append(f"  Qualification:  {result.qualification_major or '(not found)'}")
    lines.append(f"  Exp. Years:     {result.experience_years_estimate if result.experience_years_estimate is not None else '(not found)'}")
    lines.append(f"  Skills:         {', '.join(result.skills) if result.skills else '(none)'}")
    lines.append(f"  Certifications: {', '.join(result.certifications) if result.certifications else '(none)'}")
    lines.append(f"  Raw text length: {len(result.raw_text)} chars")
    lines.append("=" * 70)
    return "\n".join(lines)


def main():
    """Process CV files and display extraction results."""
    args = sys.argv[1:]

    if args:
        # Process specific files provided as arguments
        files = [Path(arg) for arg in args]
    else:
        # Default: process all files in tests/synthetic_cvs/
        synthetic_dir = PROJECT_ROOT / "tests" / "synthetic_cvs"
        if not synthetic_dir.exists():
            print(f"Synthetic CV directory not found: {synthetic_dir}")
            print("Run 'python scripts/generate_synthetic_cvs.py' first.")
            return
        files = sorted(synthetic_dir.iterdir())

    if not files:
        print("No files to process.")
        return

    print(f"\n{'=' * 70}")
    print(f"  SkillsSort CV Extraction POC")
    print(f"  Processing {len(files)} file(s)")
    print(f"{'=' * 70}\n")

    success_count = 0
    partial_count = 0
    failed_count = 0

    for filepath in files:
        if not filepath.is_file():
            continue

        result = extract_from_file(filepath)
        print(format_result(filepath, result))
        print()

        if result.parsing_status == "success":
            success_count += 1
        elif result.parsing_status == "partial":
            partial_count += 1
        else:
            failed_count += 1

    # Summary
    print("\n" + "=" * 70)
    print("  SUMMARY")
    print("=" * 70)
    print(f"  Total files:    {success_count + partial_count + failed_count}")
    print(f"  Success:        {success_count}")
    print(f"  Partial:        {partial_count}")
    print(f"  Failed:         {failed_count}")
    print("=" * 70)


if __name__ == "__main__":
    main()

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ExtractionResult:
    """
    Standardized data contract output for CV text extraction.
    Developer 2's parser must return this structure.
    """

    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    institution: Optional[str] = None
    qualification_major: Optional[str] = None
    experience_years_estimate: Optional[float] = None
    skills: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    raw_text: str = ""
    parsing_status: str = "success"  # options: success, partial, failed
    uncertain_fields: List[str] = field(
        default_factory=list
    )  # fields needing human review
    error_message: Optional[str] = None

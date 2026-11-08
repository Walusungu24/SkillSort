# SkillsSort

SkillsSort is a recruitment-support application intended to reduce the time spent
manually reviewing CVs. It aims to extract selected information from CVs and present
it in an organized, sortable format so recruitment staff can review applicants more
efficiently.

## Project status

Early planning and technical proof-of-concept stage. The current requirements are
provisional while the recruitment workflow and Excel fields are confirmed with the
stakeholder.

## Initial goals

- Upload multiple CVs.
- Extract selected information from supported documents.
- Present results in a sortable and searchable table.
- Keep a secure reference to each original CV.
- Support recruiter review; do not automatically reject applicants.
- Export agreed fields to a spreadsheet format if confirmed in the MVP.

## Proposed technology

Python, Django, and PostgreSQL are the current working direction. The team will
record final technology decisions in `docs/decisions/decision-log.md`.

## Setup

### Prerequisites

- Python 3.11+ (Python 3.12 recommended)
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/Walusungu24/SkillSort.git
cd SkillSort

# Create and activate a virtual environment
python -m venv venv

# Windows (PowerShell)
.\venv\Scripts\Activate

# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your local database URL and secret key

# Run database migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

The app will be available at `http://127.0.0.1:8000/`.

## Development workflow

- Keep `main` stable.
- Work on small feature branches (e.g., `feature/cv-extraction`).
- Open pull requests and request a teammate review.
- Add or update tests and documentation with meaningful changes.
- Use clear commit messages: `feat:`, `fix:`, `test:`, `docs:`, `chore:`, `deps:`.

## Privacy and security

Use synthetic CVs during development. Do not commit real applicant CVs,
spreadsheets containing personal information, secrets, or `.env` files.
Use real applicant data only after authorization and safeguards are confirmed.

## Documentation

See `docs/` for requirements, architecture, decisions, testing strategy, roadmap,
and backlog.

## Team

- **Developer 1** — Backend, database, and integration coordination
- **Developer 2** — CV processing and data analysis
- **Developer 3** — Interface and workflow

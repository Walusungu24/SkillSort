# Experience Calculation Rules & Edge Cases

**Author:** Developer 2 — CV Processing & Information Extraction
**Date:** November 2026

---

## Overview

The extractor calculates an estimated total duration of work experience by
parsing date ranges from CV text. This document explains the rules, how edge
cases are handled, and known limitations.

---

## Date Range Detection

### Supported Formats

The regex matches the following date range patterns:

| Format | Example | Parsed As |
|--------|---------|-----------|
| Month Year – Month Year | `Jan 2021 – Dec 2023` | Jan 2021 to Dec 2023 |
| Month Year – Present | `Mar 2020 – Present` | Mar 2020 to current date |
| Year – Year | `2019 - 2021` | Jan 2019 to Dec 2021 (month defaults) |
| Year – Present/Now/Current | `2021 - now` | Jan 2021 to current date |

Month abbreviations and full names are both supported:
`Jan/January`, `Feb/February`, `Mar/March`, ... `Dec/December`.

Separators can be hyphens (`-`) or en-dashes (`–`) with optional surrounding spaces.

### How "Present" is Resolved

When the end date is `Present`, `Now`, or `Current`, the parser substitutes
the current system date (year and month). As of testing in November 2026,
"Present" resolves to November 2026.

**Implication:** Experience estimates for current roles will change over time.
This is expected behavior — the estimate reflects experience as of the date
the CV is processed.

### How Months Are Mapped

Month names are converted to numeric values (1–12) for fractional year
calculation:

```
January = 1, February = 2, ..., December = 12
```

### Duration Calculation Formula

```
duration = (end_year - start_year) + (end_month - start_month) / 12
```

Rounded to 2 decimal places.

**Example:** Jan 2021 to Dec 2023
```
duration = (2023 - 2021) + (12 - 1) / 12 = 2 + 0.92 = 2.92 years
```

---

## Edge Cases

### 1. Overlapping Employment Periods

**Scenario:** A candidate holds two jobs simultaneously, e.g.:
```
HR Assistant, Global Services, Feb 2022 – Aug 2023
Recruitment Intern, TalentHub, Jan 2022 – Jun 2022  ← overlaps with above
```

**Current behavior:**
- Both durations are calculated and summed independently
- The overlap (Jan 2022 – Jun 2022) is counted twice in the total
- The system detects the overlap and adds `experience_years_estimate` to
  `uncertain_fields`

**Detection logic:** For each pair of date ranges, if the start of one falls
within the span of another, an overlap is flagged:
```python
if start1 <= end2 and start2 <= end1:
    has_overlap = True
```

**Result in cv3:** 5.17 years estimated (actual non-overlapping total ~4.5 years)

**Future improvement:** Calculate the union of date ranges to avoid
double-counting overlap periods.

---

### 2. Year-Only Dates (No Month Specified)

**Scenario:** A CV only provides years, e.g.:
```
IT Support Officer, DataSys, 2019 - 2021
Systems Administrator, NetCore, 2021 - now
```

**Current behavior:**
- Start month defaults to January (1)
- End month defaults to December (12), or current month for "Present"

**Result in cv5:**
- "2019 - 2021" → Jan 2019 to Dec 2021 = 2.92 years (actual: 2 years)
- "2021 - now" → Jan 2021 to Nov 2026 = 5.83 years (actual: 5 years)
- Total: 8.84 years (actual: ~7 years) — inflated by ~1.84 years

**Why it's inflated:** Assuming January-to-December adds fractional months
that don't exist in year-only date ranges.

**Flagging:** These cases are added to `uncertain_fields` when the overlap
detection triggers, but year-only inflation is not currently detected
separately.

**Future improvement:** For year-only dates, use whole-year calculation:
`end_year - start_year` without fractional month logic.

---

### 3. Missing Dates

**Scenario:** A CV lists employment history without any dates.

**Current behavior:**
- No date ranges are detected
- `experience_years_estimate` is set to `None`
- `experience_years_estimate` is added to `uncertain_fields`
- Parsing status is not affected (can still be "success" if other fields are present)

---

### 4. Single Employment Entry

**Scenario:** A CV has one job with a clear date range.

**Current behavior:**
- Duration is calculated normally
- No overlap possible (only one range)
- Typically results in accurate estimate

---

### 5. Date Ranges with Start After End

**Scenario:** Malformed date range like "Dec 2023 – Jan 2021".

**Current behavior:**
- The parser checks `if end_year < start_year: continue` and skips the range
- No error is raised; the range is silently ignored
- If this was the only date range, `experience_years_estimate` will be `None`

---

## Summary of Uncertainty Flags

| Condition | Flagged in `uncertain_fields`? |
|-----------|-------------------------------|
| Overlapping date ranges detected | ✅ Yes |
| No date ranges found at all | ✅ Yes |
| Year-only dates (no month precision) | ⚠️ Only if overlap also detected |
| Date range with start after end | No (silently skipped) |
| "Present" resolved to current date | No (expected behavior, not uncertain) |

---

## What the Extractor Does NOT Do

Per the roadmap's guidance to "document uncertain cases rather than guessing":

- **Does not guess dates** — If no dates are found, the estimate is `None`
- **Does not infer experience from job titles** — A "Senior Developer" title
  does not imply more years of experience
- **Does not count internships differently** — Internships with dates are
  treated the same as full employment
- **Does not account for career gaps** — Gaps between jobs are not subtracted
  from the total
- **Does not weight part-time vs full-time** — All durations are treated as
  full-time equivalents

These decisions are deliberate. The system surfaces what it can calculate
and flags uncertainty rather than making assumptions that could mislead
recruiters.

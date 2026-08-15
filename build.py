from pathlib import Path
from datetime import date
import calendar

import yaml
from jinja2 import Environment, FileSystemLoader


# --------------------------------------------------
# Paths
# --------------------------------------------------

ROOT = Path(__file__).parent

SITE_FILE = ROOT / "site.yaml"
TEMPLATE_DIR = ROOT / "templates"
OUTPUT_FILE = ROOT / "index.html"


# --------------------------------------------------
# Dutch date formatting
# --------------------------------------------------

DUTCH_MONTHS = [
    "januari",
    "februari",
    "maart",
    "april",
    "mei",
    "juni",
    "juli",
    "augustus",
    "september",
    "oktober",
    "november",
    "december",
]


def format_date(date_value):
    """
    Convert a YAML date into several useful formats.

    Example:
        2026-09-01

    becomes:
        full:       1 september 2026
        uppercase:  1 SEPTEMBER 2026
        short:      1.9.2026
    """

    if isinstance(date_value, date):
        event_date = date_value
    else:
        event_date = date.fromisoformat(str(date_value))

    day = event_date.day
    month = DUTCH_MONTHS[event_date.month - 1]
    year = event_date.year

    return {
        "full": f"{day} {month} {year}",
        "uppercase": f"{day} {month.upper()} {year}",
        "short": f"{day} {event_date.month} {year}",
        "day": str(day),
        "month": month.upper(),
        "year": str(year),
    }


# --------------------------------------------------
# Load YAML
# --------------------------------------------------

with open(SITE_FILE, "r", encoding="utf-8") as file:
    site = yaml.safe_load(file)


# --------------------------------------------------
# Prepare event data
# --------------------------------------------------

site["event"]["date_formatted"] = format_date(
    site["event"]["date"]
)


# --------------------------------------------------
# Load Jinja template
# --------------------------------------------------

environment = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=True,
)

template = environment.get_template("index.html")


# --------------------------------------------------
# Generate website
# --------------------------------------------------

html = template.render(**site)

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    file.write(html)


print(f"Website gegenereerd: {OUTPUT_FILE}")
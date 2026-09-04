from pathlib import Path
from datetime import date, datetime
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

import yaml
from jinja2 import Environment, FileSystemLoader


# --------------------------------------------------
# Paths
# --------------------------------------------------

ROOT = Path(__file__).parent

SITE_FILE = ROOT / "site.yaml"
TEMPLATE_DIR = ROOT / "templates"

OUTPUT_FILE = ROOT / "index.html"
ROBOTS_FILE = ROOT / "robots.txt"
SITEMAP_FILE = ROOT / "sitemap.xml"


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
        short:      1 9 2026
        day:        1
        month:      SEPTEMBER
        year:       2026
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

event_date = date.fromisoformat(str(site["event"]["date"]))
event_timezone = ZoneInfo(site["event"].get("timezone", "Europe/Amsterdam"))

for datetime_key, time_key in (
    ("start_datetime", "start_time"),
    ("end_datetime", "end_time"),
):
    event_datetime = datetime.combine(
        event_date,
        datetime.strptime(site["event"][time_key], "%H:%M").time(),
        tzinfo=event_timezone,
    )
    site["event"][datetime_key] = event_datetime.isoformat()

site["event"]["price_value"] = 0 if str(site["event"]["price"]).lower() == "gratis" else site["event"]["price"]

for upcoming_event in site.get("upcoming_events", []):
    upcoming_event["date_formatted"] = format_date(upcoming_event["date"])

# --------------------------------------------------
# Derived site information
# --------------------------------------------------

site_url = site["site"].get("url", "").rstrip("/")

site["site"]["canonical_url"] = site_url


# --------------------------------------------------
# Jinja environment
# --------------------------------------------------

environment = Environment(
    loader=FileSystemLoader(TEMPLATE_DIR),
    autoescape=True,
)

template = environment.get_template("index.html")


# --------------------------------------------------
# Generate HTML
# --------------------------------------------------

html = template.render(**site)

with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
    file.write(html)


# --------------------------------------------------
# Generate robots.txt
# --------------------------------------------------

if site_url:

    robots = f"""User-agent: *
Allow: /

Sitemap: {urljoin(site_url + "/", "sitemap.xml")}
"""

else:

    robots = """User-agent: *
Allow: /
"""


with open(ROBOTS_FILE, "w", encoding="utf-8") as file:
    file.write(robots)


# --------------------------------------------------
# Generate sitemap.xml
# --------------------------------------------------

if site_url:

    sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>{site_url}/</loc>
    </url>
</urlset>
"""

    with open(SITEMAP_FILE, "w", encoding="utf-8") as file:
        file.write(sitemap)


# --------------------------------------------------
# Done
# --------------------------------------------------

print("Website gegenereerd.")
print(f"HTML:      {OUTPUT_FILE}")

if site_url:
    print(f"Robots:    {ROBOTS_FILE}")
    print(f"Sitemap:   {SITEMAP_FILE}")
else:
    print("Robots.txt gegenereerd.")
    print("Sitemap wordt pas gegenereerd zodra site.url is ingevuld.")
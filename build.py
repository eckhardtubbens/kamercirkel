from pathlib import Path
from datetime import date, datetime
import json
from copy import deepcopy
from urllib.parse import urljoin, urlsplit
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
TICKET_EVENTS_FILE = ROOT / "ticket-events.yaml"
TICKET_EVENTS_JSON_FILE = ROOT / "ticket-events.json"


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


def json_default(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    raise TypeError(f"Niet JSON-serialiseerbare waarde: {value!r}")


# --------------------------------------------------
# Load YAML
# --------------------------------------------------

with open(SITE_FILE, "r", encoding="utf-8") as file:
    site = yaml.safe_load(file)


# --------------------------------------------------
# Load central concert data
# --------------------------------------------------

with open(TICKET_EVENTS_FILE, "r", encoding="utf-8") as file:
    ticket_events_data = yaml.safe_load(file)

if not isinstance(ticket_events_data, dict):
    raise ValueError("ticket-events.yaml moet een YAML-object bevatten.")

ticket_events = ticket_events_data.get("events")
payment_links = ticket_events_data.get("payment_links")

if not isinstance(ticket_events, list) or not ticket_events:
    raise ValueError("ticket-events.yaml moet een niet-lege events-lijst bevatten.")

if not isinstance(payment_links, dict) or not payment_links:
    raise ValueError("ticket-events.yaml moet payment_links met vaste betaalbedragen bevatten.")

shared_event_fields = site.get("event", {})
for field in ("title", "timezone", "location", "max_tickets_per_order"):
    if not shared_event_fields.get(field):
        raise ValueError(f"site.yaml moet event.{field} bevatten.")

max_tickets_per_order = shared_event_fields["max_tickets_per_order"]
if not isinstance(max_tickets_per_order, int) or max_tickets_per_order <= 0:
    raise ValueError("event.max_tickets_per_order in site.yaml moet positief zijn.")

for amount, payment_url in payment_links.items():
    parsed_payment_url = urlsplit(str(payment_url))
    if (
        not str(amount).replace(".", "", 1).isdigit()
        or float(amount) <= 0
        or parsed_payment_url.scheme != "https"
        or parsed_payment_url.netloc.lower() != "bunq.me"
        or not parsed_payment_url.path.startswith("/o/")
        or parsed_payment_url.path == "/o/"
    ):
        raise ValueError(f"Ongeldige vaste bunq-betaallink voor bedrag {amount!r}.")

public_ticket_events_data = deepcopy(ticket_events_data)
public_ticket_events_data["payment_links"] = {
    str(amount): payment_url for amount, payment_url in payment_links.items()
}

seen_ticket_event_ids = set()

for ticket_event in ticket_events:
    required_fields = (
        "date",
        "start_time",
        "end_time",
        "price",
    )
    missing_fields = [field for field in required_fields if field not in ticket_event]

    if missing_fields:
        raise ValueError(
            f"Concertrecord mist velden {', '.join(missing_fields)}: {ticket_event}"
        )

    event_date = date.fromisoformat(str(ticket_event["date"]))
    event_id = event_date.isoformat()

    if event_id in seen_ticket_event_ids:
        raise ValueError(f"De concertdatum is dubbel: {event_id}.")

    ticket_event["id"] = event_id
    ticket_event["title"] = shared_event_fields["title"]
    ticket_event["timezone"] = shared_event_fields["timezone"]
    ticket_event["location"] = deepcopy(shared_event_fields["location"])
    ticket_event["max_tickets_per_order"] = max_tickets_per_order
    seen_ticket_event_ids.add(event_id)
    ticket_event["date_formatted"] = format_date(event_date)
    ticket_event["date_label"] = ticket_event["date_formatted"]["full"]
    ticket_event["label"] = (
        f"{ticket_event['date_label']} · {ticket_event['location']['name']}"
    )

    if not isinstance(ticket_event["price"], (int, float)) or ticket_event["price"] < 0:
        raise ValueError(f"Ticketprijs mag niet negatief zijn voor {event_id}.")

    for time_key in ("start_time", "end_time"):
        datetime.strptime(ticket_event[time_key], "%H:%M")

    event_timezone = ZoneInfo(ticket_event["timezone"])
    for datetime_key, time_key in (
        ("start_datetime", "start_time"),
        ("end_datetime", "end_time"),
    ):
        event_datetime = datetime.combine(
            event_date,
            datetime.strptime(ticket_event[time_key], "%H:%M").time(),
            tzinfo=event_timezone,
        )
        ticket_event[datetime_key] = event_datetime.isoformat()

today = datetime.now(ZoneInfo(shared_event_fields["timezone"])).date()
upcoming_events = sorted(
    (item for item in ticket_events if date.fromisoformat(item["date"]) >= today),
    key=lambda item: item["date"],
)
active_event = upcoming_events[0] if upcoming_events else None

if active_event is None:
    raise ValueError("ticket-events.yaml bevat geen concerten op of na vandaag.")

for ticket_event in ticket_events:
    programme = ticket_event.get("programme") or []
    if not isinstance(programme, list):
        raise ValueError(f"Het programma moet een lijst zijn voor {ticket_event['id']}.")
    ticket_event["programme"] = programme

ticket_events.sort(key=lambda item: item["date"])
public_ticket_events_data["events"] = sorted(
    [
        {
            key: value
            for key, value in ticket_event.items()
            if key not in ("date_formatted", "date_label", "label", "start_datetime", "end_datetime")
        }
        for ticket_event in ticket_events
    ],
    key=lambda item: str(item["date"]),
)

with open(TICKET_EVENTS_JSON_FILE, "w", encoding="utf-8") as file:
    json.dump(
        public_ticket_events_data,
        file,
        ensure_ascii=False,
        indent=2,
        default=json_default,
    )
    file.write("\n")

for field in (
    "title",
    "date",
    "date_formatted",
    "start_time",
    "end_time",
    "timezone",
    "start_datetime",
    "end_datetime",
    "location",
    "price",
    "programme",
):
    site["event"][field] = active_event[field]

site["event"]["price_label"] = (
    "vrije bijdrage" if active_event["price"] == 0 else str(active_event["price"])
)
site["event"]["price_value"] = active_event["price"]
site["ticket_events"] = ticket_events
site["upcoming_events"] = upcoming_events

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
    print(f"Ticketbron: {TICKET_EVENTS_FILE}")
    print(f"Ticketfeed: {TICKET_EVENTS_JSON_FILE}")
else:
    print("Robots.txt gegenereerd.")
    print("Sitemap wordt pas gegenereerd zodra site.url is ingevuld.")
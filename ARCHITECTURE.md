# Kamercirkel — Architecture & Development Documentation

> This document is the authoritative technical documentation for the Kamercirkel website.
>
> It describes the intended architecture, current development workflow, deployment model, content model and future direction. When the implementation changes, update this document.

---

## 1. Project purpose

Kamercirkel is a Dutch cultural initiative and open stage for classical chamber music in Amsterdam.

The concept is aimed primarily at:

- chamber music ensembles that want to perform for an audience;
- experienced amateur and professional musicians;
- musicians who want to meet other musicians and potentially form an ensemble;
- listeners interested in classical chamber music.

The website deliberately communicates the concept in a minimal and direct way.

The site should feel contemporary and slightly underground rather than like a conventional institutional classical-music website.

The website is not intended to be a complex web application. It is a lightweight static site with automated generation and deployment.

---

## 2. High-level architecture

The core architecture is:

```text
                    CONTENT
                       │
                       ▼
                  site.yaml
                       │
                       ▼
                    build.py
                       │
                       ▼
                Jinja2 template
                       │
                       ▼
              generated static HTML
                       │
                       ▼
                GitHub Actions
                       │
                       ▼
                 GitHub Pages
                       │
                       ▼
              https://kamercirkel.nl
```

The main principle is separation of responsibilities:

```text
site.yaml
    = content and event configuration

build.py
    = data loading, formatting and build logic

templates/index.html
    = HTML structure and Jinja presentation logic

css/style.css
    = visual design and responsive layout

.github/workflows/
    = CI/CD and deployment

ARCHITECTURE.md
    = technical documentation
```

This architecture intentionally avoids a database, CMS and backend server.

---

## 3. Repository

The GitHub repository is:

```text
https://github.com/eckhardtubbens/kamercirkel
```

The local Windows development directory is currently:

```text
C:\Users\eckha\Projects\kamercirkel
```

The production website is intended to use:

```text
https://kamercirkel.nl
```

The GitHub Pages URL may also exist as the underlying Pages address:

```text
https://eckhardtubbens.github.io/kamercirkel/
```

The custom domain is the public/canonical address.

---

## 4. Repository structure

The conceptual repository structure is:

```text
kamercirkel/
│
├── .github/
│   ├── copilot-instructions.md
│   └── workflows/
│       └── ...
│
├── css/
│   └── style.css
│
├── templates/
│   └── index.html
│
├── site.yaml
├── build.py
├── ARCHITECTURE.md
├── README.md
├── .gitignore
└── ...
```

Additional files may include:

```text
sitemap.xml
robots.txt
images/
```

or other generated/static assets as the project develops.

The actual repository contents are authoritative if they differ from this conceptual structure.

---

## 5. `site.yaml`

`site.yaml` is the central source for editable website and event content.

The reason for this file is to avoid having to edit the HTML template every time event information changes.

Typical content includes:

```yaml
site:
  name: "Kamercirkel"
  tagline: "Open podium voor kamermuziek"
  city: "Amsterdam"
  canonical_url: "https://kamercirkel.nl"

event:
  title: "Open podium voor kamermuziek"
  date: "2026-09-01"

  start_datetime: "2026-09-01T19:00:00+02:00"
  end_datetime: "2026-09-01T22:00:00+02:00"

  location:
    name: "Zaal 100"
    address: "De Wittenstraat 100"
    postal_code: "1052 BA"
    city: "Amsterdam"
    map_url: "..."

  price: 5

  text:
    introduction: "..."
    musicians: "..."
    listeners: "..."

  registration:
    url: "..."

social:
  instagram: "..."
  whatsapp: "..."
```

The exact current schema should always be checked against the actual `site.yaml`.

### Principle

Content belongs in YAML.

Examples:

- names;
- descriptions;
- dates;
- times;
- locations;
- prices;
- registration links;
- social links;
- programme data when programme data is locally managed.

Design values do not need to be placed in YAML. The visual design remains in CSS.

---

## 6. `build.py`

`build.py` is the Python build script.

Its responsibilities include:

1. reading `site.yaml`;
2. loading the Jinja2 template;
3. preparing derived values;
4. formatting event dates for human display;
5. rendering the HTML;
6. writing the generated website;
7. optionally generating other static files such as sitemap or robots.txt when implemented.

The build script should contain build logic rather than ordinary website copy.

Bad:

```python
title = "Open podium voor kamermuziek"
```

Preferred:

```python
title = site["event"]["title"]
```

with the value stored in `site.yaml`.

### Local build

Run:

```powershell
python build.py
```

A successful build should complete without a traceback.

If the project generates output files that are used for deployment, inspect those files before committing.

---

## 7. Jinja2 template

The main HTML template is:

```text
templates/index.html
```

It is rendered by Jinja2.

Example:

```jinja2
<h1>
    {{ event.title }}
</h1>
```

The template defines page structure while values come from the YAML/build context.

Do not use the template as a second content database.

Avoid hard-coding values such as:

- event dates;
- addresses;
- prices;
- registration URLs;
- social URLs;
- programme data;

when those values already exist in `site.yaml`.

---

## 8. CSS

The main stylesheet is:

```text
css/style.css
```

CSS is the authoritative location for visual design.

It controls:

- typography;
- spacing;
- layout;
- borders;
- colours;
- responsive behaviour;
- mobile layout;
- sizing;
- visual hierarchy.

The project intentionally keeps the design in CSS rather than creating a YAML-based design system.

This is a usability choice: content changes frequently, whereas design changes are less frequent and are better handled directly in CSS.

---

## 9. Design philosophy

The website should remain:

- minimal;
- typographic;
- direct;
- spacious;
- fast;
- mobile-friendly;
- contemporary;
- slightly underground;
- professional enough for serious classical musicians.

The site should create curiosity without becoming cryptic.

It should not look like:

- a generic festival template;
- a corporate event platform;
- a conventional WordPress website;
- an overly formal institutional classical-music site.

At the same time, the copy should not become so informal that experienced professional musicians feel excluded.

The concept should communicate that ensembles with substantial musical experience are welcome, without requiring a specific professional status.

---

## 10. Current event

The first open podium is currently configured for:

```text
Date:
1 September 2026

Location:
Zaal 100
De Wittenstraat 100
1052 BA Amsterdam

Price:
€5

Feature:
The large hall contains a grand piano.
```

The exact event date, times, price and copy must be taken from `site.yaml` rather than assumed from this document.

---

## 11. Date handling

Dates should be stored in a machine-readable format where possible:

```yaml
date: "2026-09-01"
```

The build process can derive human-readable formats.

Dutch display should avoid unnecessary leading zeroes.

Preferred:

```text
1 september 2026
```

not:

```text
01 september 2026
```

The compact date in the header should display:

```text
1 9 2026
```

not:

```text
01 09 2026
```

This is an explicit design/content requirement.

---

## 12. Event start and end time

The event should have explicit start and end datetimes.

Example:

```yaml
start_datetime: "2026-09-01T19:00:00+02:00"
end_datetime: "2026-09-01T22:00:00+02:00"
```

These values have two purposes:

1. displaying the event time to users;
2. supplying correct Schema.org structured data.

The visible page should show the event time.

The structured data should use ISO-compatible datetime values with the correct timezone.

Do not maintain a different time in the HTML and structured data.

---

## 13. Event content

The event description should explain that Kamercirkel is:

- an open stage for classical chamber music;
- a place where ensembles can perform for an audience;
- open to musicians with different professional and musical backgrounds;
- a place where musicians can meet other musicians;
- also open to listeners.

The copy should be professional and welcoming.

Avoid unnecessarily informal expressions such as implying that musicians are only welcome if they have "something in their fingers". The goal is to communicate musical ability and seriousness without excluding experienced professionals.

---

## 14. Registration

The registration system uses Google Forms.

The form is intended to allow ensembles to register before an event so that participating musicians have confidence that they will have a meaningful opportunity to perform.

The form may collect:

- ensemble name;
- contact person;
- e-mail address;
- telephone number;
- names of musicians;
- instruments;
- composer;
- piece;
- estimated duration;
- additional notes.

The current Google Form URL is stored in `site.yaml`.

The website should not hard-code the form URL.

---

## 15. Google Forms and Google Sheets

The intended data flow is:

```text
Musician / ensemble
        │
        ▼
Google Form
        │
        ▼
Google Sheet
        │
        ▼
event administration
        │
        ▼
approved programme
        │
        ▼
website
```

The long-term objective is to automate as much of this as practical.

However, automation must not be assumed to exist simply because it is planned.

Before implementing automatic publication, there should be an approval/status mechanism.

A possible model is:

```text
new
confirmed
rejected
```

Only confirmed entries should normally become public.

---

## 16. Provisional programme

The upcoming event should display a provisional programme.

A programme item may contain:

```text
time
ensemble
musicians
instruments
composer
piece
duration
```

The website should clearly label the programme as provisional if it is not final.

Potential future workflow:

```text
Google Form
     ↓
Google Sheet
     ↓
approved rows
     ↓
programme data
     ↓
build.py
     ↓
Jinja template
     ↓
static website
```

The exact implementation should be chosen based on the simplest reliable solution.

Do not introduce a backend database unless there is a demonstrated need.

---

## 17. Programme publication safety

Submitted participant information is not automatically public information.

Before publishing:

- verify the ensemble;
- verify the programme item;
- verify spelling of musician names;
- verify composer and piece;
- confirm publication is appropriate.

The website should not expose personal contact information from registration forms.

Only information intended for public programme display should be published.

---

## 18. SEO

The website should be discoverable through normal search engines.

Important SEO elements include:

- descriptive `<title>`;
- meta description;
- canonical URL;
- semantic HTML;
- event structured data;
- organization information;
- sitemap;
- robots.txt.

The homepage should explicitly contain meaningful words such as:

- Kamercirkel;
- klassieke kamermuziek;
- open podium;
- Amsterdam;
- ensembles;
- musici;
- luisteraars.

Important information should exist as normal HTML text.

Do not rely solely on JavaScript, images or CSS-generated content.

---

## 19. LLM and AI discoverability

The website should also be understandable by AI/LLM systems.

The same principles that help normal search engines are useful here:

- clear semantic HTML;
- explicit names;
- explicit dates;
- explicit location;
- explicit event purpose;
- descriptive text;
- structured data;
- canonical URL;
- sitemap.

Avoid hiding important information behind interaction or client-side rendering.

A machine reading the raw HTML should be able to determine:

- what Kamercirkel is;
- where it takes place;
- when it takes place;
- who it is for;
- how musicians can register;
- whether listeners can attend.

---

## 20. Structured data

The event should use Schema.org structured data.

Conceptually:

```json
{
  "@context": "https://schema.org",
  "@type": "Event",
  "name": "...",
  "description": "...",
  "startDate": "...",
  "endDate": "...",
  "eventStatus": "https://schema.org/EventScheduled",
  "location": {
    "@type": "Place",
    "name": "...",
    "address": {
      "@type": "PostalAddress",
      "streetAddress": "...",
      "postalCode": "...",
      "addressLocality": "...",
      "addressCountry": "NL"
    }
  },
  "offers": {
    "@type": "Offer",
    "price": 5,
    "priceCurrency": "EUR"
  }
}
```

The actual template should derive values from the event configuration.

When changing:

- date;
- time;
- location;
- price;
- event title;

verify the structured data as well.

---

## 21. Open Graph

The page should include Open Graph metadata so links shared through messaging and social media have useful previews.

Important fields include:

- `og:type`;
- `og:title`;
- `og:description`;
- `og:url`;
- `og:locale`.

A social preview image may be added later.

---

## 22. Canonical URL

The intended canonical production URL is:

```text
https://kamercirkel.nl
```

It should be configured centrally in `site.yaml`.

The template should use the configured canonical URL rather than hard-coding it in multiple places.

The canonical URL is also used for Open Graph and organization/event metadata where appropriate.

---

## 23. Domain and DNS

The domain is registered separately from website hosting.

Current registrar:

```text
mijn.host
```

The website is hosted by GitHub Pages.

The intended architecture is:

```text
kamercirkel.nl
      │
      │ DNS
      ▼
GitHub Pages
      │
      ▼
Kamercirkel website
```

GitHub Pages uses four A records for the apex domain:

```text
185.199.108.153
185.199.109.153
185.199.110.153
185.199.111.153
```

The `www` hostname uses a CNAME pointing to:

```text
eckhardtubbens.github.io
```

DNS records used for e-mail, such as MX, SPF and DMARC records, must remain intact.

Do not remove mail-related DNS records when changing website DNS.

Avoid unnecessary wildcard DNS records.

---

## 24. HTTPS

The production site should use:

```text
https://kamercirkel.nl
```

GitHub Pages provides HTTPS for the custom domain once DNS and domain configuration are correctly established.

The GitHub Pages setting for enforcing HTTPS should be enabled when available.

Do not implement a separate TLS certificate or reverse proxy unless the architecture changes.

---

## 25. GitHub Pages

GitHub Pages is the hosting platform.

The source repository is:

```text
https://github.com/eckhardtubbens/kamercirkel
```

The site is deployed automatically.

The GitHub Pages URL is an implementation URL; the custom domain is the public canonical URL.

---

## 26. GitHub Actions

GitHub Actions builds and deploys the site automatically.

Conceptual workflow:

```text
local source change
        │
        ▼
git push
        │
        ▼
GitHub repository
        │
        ▼
GitHub Actions
        │
        ├── checkout
        ├── install Python dependencies
        ├── run build.py
        └── deploy
        │
        ▼
GitHub Pages
```

The exact workflow filename and action versions should be taken from `.github/workflows/`.

Do not assume the workflow implementation from this document alone.

If the workflow changes, update this document.

---

## 27. Git workflow

Normal local workflow:

```powershell
cd C:\Users\eckha\Projects\kamercirkel

python build.py

git status

git add .

git commit -m "Describe the change"

git push
```

After pushing:

1. inspect GitHub Actions;
2. wait for deployment;
3. inspect the production website.

Do not make unrelated changes in the same commit when avoidable.

Use meaningful commit messages.

---

## 28. Local development

The project is developed locally on Windows.

Current development environment:

```text
Windows
Python 3.13.3
Git 2.49.0.windows.1
```

The local project directory is:

```text
C:\Users\eckha\Projects\kamercirkel
```

Build locally with:

```powershell
python build.py
```

The generated site can be served locally with a simple HTTP server when needed.

Example:

```powershell
python -m http.server 8000
```

The exact directory from which this command should be run depends on where the generated static output is written.

The site can be tested from another device on the home network using the laptop's local IP address, for example:

```text
http://192.168.1.91:8000
```

The local IP address is not guaranteed to remain the same.

---

## 29. Dependencies

The project intentionally uses a small dependency set.

Core Python dependencies are:

- Jinja2;
- PyYAML.

The exact dependency installation mechanism should be taken from the repository's current workflow/files.

Do not add a dependency for functionality that can reasonably be implemented using the standard library or existing project dependencies.

Avoid:

- frontend frameworks;
- CMS platforms;
- databases;
- backend frameworks;
- large JavaScript bundles.

unless explicitly justified.

---

## 30. Images and static assets

Images can be added to the website.

A future/static structure may be:

```text
images/
├── ...
```

Images should:

- have meaningful filenames;
- have appropriate alt text;
- be optimized for web use;
- not unnecessarily increase page size.

Potential future uses include:

- event photography;
- venue photography;
- ensemble photography;
- visual identity;
- social sharing images.

Do not add images merely for decoration if they reduce the clarity of the minimalist design.

---

## 31. Accessibility

The site should use semantic HTML where possible.

Important practices:

- meaningful headings;
- accessible links;
- useful alt text for meaningful images;
- sufficient contrast;
- logical document order;
- mobile usability;
- visible focus states where appropriate.

Do not sacrifice accessibility for the underground visual style.

---

## 32. Responsive design

The website must work on:

- desktop;
- laptop;
- tablet;
- mobile.

The existing CSS contains responsive rules.

Mobile design is particularly important because event links may be shared through WhatsApp and opened on phones.

When changing desktop layout, check whether the mobile layout remains coherent.

---

## 33. Content editing workflow

For ordinary event changes:

```text
edit site.yaml
      ↓
python build.py
      ↓
test locally
      ↓
git add .
      ↓
git commit
      ↓
git push
      ↓
GitHub Actions
      ↓
live website
```

The goal is that routine content management does not require editing HTML.

---

## 34. When to edit which file

### Change content

Edit:

```text
site.yaml
```

Examples:

- date;
- time;
- price;
- address;
- description;
- registration URL;
- Instagram URL.

### Change visual design

Edit:

```text
css/style.css
```

Examples:

- spacing;
- typography;
- colours;
- mobile layout;
- borders.

### Change page structure

Edit:

```text
templates/index.html
```

Examples:

- add a programme section;
- reorder sections;
- add a new information block.

### Change data processing

Edit:

```text
build.py
```

Examples:

- date formatting;
- programme transformation;
- generated files;
- sitemap generation.

### Change deployment

Edit:

```text
.github/workflows/
```

Examples:

- Python version;
- dependencies;
- build command;
- deployment configuration.

### Change project instructions

Edit:

```text
.github/copilot-instructions.md
```

### Change technical documentation

Edit:

```text
ARCHITECTURE.md
```

---

## 35. Copilot instructions

Repository-wide Copilot instructions are stored at:

```text
.github/copilot-instructions.md
```

The instructions tell Copilot to preserve the architecture and consult this document.

The architecture document is the detailed source of technical context.

If a new architectural decision becomes important enough that future development depends on it, document it here.

---

## 36. README

`README.md` should remain concise.

It should provide:

- project purpose;
- local build instructions;
- repository URL;
- link/reference to `ARCHITECTURE.md`.

Detailed implementation information belongs in this document rather than the README.

---

## 37. Deployment troubleshooting

If a local build fails:

```powershell
python build.py
```

Read the traceback first.

Common causes include:

- incorrect YAML indentation;
- missing YAML key;
- template referring to a value that does not exist;
- Python dependency missing;
- invalid Jinja syntax.

If the local build works but GitHub Actions fails:

1. open the failed workflow run;
2. inspect the first failing step;
3. compare the workflow environment with local dependencies;
4. verify that required files are committed;
5. verify that paths are correct and case-sensitive.

If GitHub Pages does not update:

1. inspect GitHub Actions;
2. confirm the workflow completed;
3. inspect Pages deployment status;
4. check whether browser caching is involved;
5. verify the generated files.

If the custom domain does not work:

1. inspect DNS at the registrar;
2. confirm the four GitHub A records;
3. confirm the `www` CNAME;
4. remove conflicting website A/AAAA records;
5. check the custom domain setting in GitHub Pages;
6. allow time for DNS propagation.

Do not change application code to solve a DNS problem.

---

## 38. Security and privacy

The website should not publish private registration data.

Do not put:

- private e-mail addresses;
- phone numbers;
- private notes;
- internal administrative information;

into public HTML unless explicitly intended.

Google Forms/Sheets may contain personal data. Treat that data as administrative information and only expose the subset intended for public programme information.

Never commit:

- passwords;
- API keys;
- access tokens;
- private credentials;
- secrets.

Use GitHub Actions secrets or another appropriate secret mechanism if future integrations require credentials.

---

## 39. Future automation

Potential improvements include:

- automatic programme generation from Google Sheets;
- programme approval workflow;
- automatic publication of confirmed participants;
- multiple event support;
- event archive;
- event-specific pages;
- sitemap generation;
- automated participant e-mails;
- reminders;
- image support;
- ensemble photographs;
- richer structured data.

These should be introduced incrementally.

The project should remain a static site unless there is a clear reason to introduce server-side infrastructure.

---

## 40. Future multi-event architecture

The current website primarily represents the next open podium.

A future structure could support:

```text
/events/
    2026-09-01/
    2026-10-...
    2026-11-...
```

or generate event pages from a structured event collection.

A future multi-event data model might look conceptually like:

```yaml
events:
  - id: "2026-09-01"
    title: "Open podium voor kamermuziek"
    date: "2026-09-01"
    ...

  - id: "2026-10-..."
    ...
```

Do not implement this complexity until multiple events actually require it.

---

## 41. Future programme architecture

A future automated programme pipeline may be:

```text
Google Form
      │
      ▼
Google Sheet
      │
      ▼
approved rows
      │
      ▼
data retrieval
      │
      ▼
build.py
      │
      ▼
Jinja template
      │
      ▼
static HTML
      │
      ▼
GitHub Actions
      │
      ▼
GitHub Pages
```

Important constraint:

The programme must not become public simply because someone submitted a form.

There should be an explicit approval step.

---

## 42. Architectural principles

### Principle 1 — Keep it simple

Do not introduce complexity without a concrete benefit.

### Principle 2 — One source for editable content

Use `site.yaml` for regularly changing content.

### Principle 3 — Keep presentation in CSS

Do not turn YAML into a design-token database unless there is a demonstrated need.

### Principle 4 — Static where possible

Prefer generating static HTML over running a backend.

### Principle 5 — Automate repetitive work

GitHub Actions should handle deployment.

Future programme automation should remove repetitive administration where practical.

### Principle 6 — Human approval for public programme data

Participant submissions should be reviewed before publication.

### Principle 7 — Document architectural changes

When the architecture changes, update this document.

### Principle 8 — Preserve professional credibility

The website should be welcoming but not amateurish.

---

## 43. Definition of done

A website change is considered complete when:

- the relevant source files have been changed;
- `python build.py` succeeds;
- the result has been inspected locally;
- mobile behaviour has been checked when relevant;
- links work;
- metadata remains correct;
- structured data remains correct where relevant;
- Git changes are committed;
- changes are pushed;
- GitHub Actions succeeds;
- the production website reflects the change.

For architectural changes, also update:

```text
ARCHITECTURE.md
.github/copilot-instructions.md
```

when appropriate.

---

## 44. Current status

The project currently has:

- a static HTML/Jinja architecture;
- a central `site.yaml`;
- a Python build script;
- a central CSS stylesheet;
- GitHub repository;
- GitHub Actions deployment;
- GitHub Pages hosting;
- custom domain configuration;
- Google Forms registration;
- a planned Google Sheets → programme workflow;
- SEO and structured-data support.

The exact state of implementation must always be checked against the repository.

This document describes the architecture and intended behaviour, not a guarantee that every future feature has already been implemented.

---

## 45. Change log for this documentation

When significant architectural decisions are made, record them here.

Example:

```text
2026-08 — Initial architecture documentation created.
2026-08 — Custom domain architecture added.
2026-08 — Google Forms / provisional programme workflow documented.
2026-08 — GitHub Actions automated deployment documented.
```

Keep this section concise.

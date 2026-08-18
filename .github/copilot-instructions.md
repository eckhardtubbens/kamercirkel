# Kamercirkel — Copilot Instructions

## Mandatory project context

Kamercirkel is a Dutch cultural initiative and open stage for classical chamber music in Amsterdam.

The website is intentionally minimal, direct, typographic and slightly underground in visual character. It is aimed primarily at musicians and ensembles, while listeners are also welcome.

Before making functional, architectural, deployment or structural changes, consult:

- `ARCHITECTURE.md`
- `site.yaml`
- `build.py`
- the relevant files in `templates/`
- `css/style.css`
- relevant files in `.github/workflows/`

`ARCHITECTURE.md` is the authoritative technical documentation of the project.

If the implementation differs from the documentation, inspect the actual repository files and treat the current code as the source of truth. If the architecture is intentionally changed, update `ARCHITECTURE.md` in the same change.

## Core architecture

Preserve the existing lightweight architecture:

    site.yaml
        ↓
    build.py
        ↓
    Jinja2 templates
        ↓
    static HTML/CSS
        ↓
    GitHub Actions
        ↓
    GitHub Pages
        ↓
    https://kamercirkel.nl

Keep responsibilities separated:

- `site.yaml` = editable content and event configuration
- `build.py` = data loading, formatting and build logic
- `templates/` = HTML structure and Jinja presentation logic
- `css/style.css` = visual design and responsive layout
- `.github/workflows/` = automated build/deployment
- `ARCHITECTURE.md` = technical documentation
- `README.md` = short human-facing project overview

## Content changes

When the user asks to change event or website content, prefer changing `site.yaml`.

Do not duplicate editable content in HTML or Python when the value can reasonably come from YAML.

Examples of content that belongs in `site.yaml`:

- site name
- tagline
- description
- city
- canonical URL
- event date
- start/end time
- location
- address
- price
- event texts
- registration URL
- social links
- programme data, when programme data is stored locally

## Visual changes

When the user asks for a visual or layout change, prefer `css/style.css`.

Do not move ordinary CSS values into YAML just to centralize them.

The visual design should remain:

- minimal
- typographic
- direct
- spacious
- fast
- mobile-friendly
- contemporary
- slightly underground
- professional enough for serious classical musicians

Do not turn the site into a generic festival, corporate or WordPress-style template.

## Structural changes

When the user asks for a change to the HTML structure, modify `templates/index.html`.

Use Jinja variables rather than hard-coded event-specific values.

When a template needs new data, first consider whether that data belongs in `site.yaml` and whether `build.py` needs to prepare or format it.

## Build logic

When the user asks for date formatting, structured data, generated pages, programme processing, sitemap generation or other data transformations, modify `build.py`.

Keep ordinary content out of Python.

Run the build locally after changes:

    python build.py

Do not consider a build change complete until the build succeeds.

## Dates and times

Event dates are stored in machine-readable form where possible.

Human-readable Dutch dates must not contain unnecessary leading zeroes.

Preferred:

    1 september 2026

and:

    1 9 2026

Not:

    01 september 2026
    01 09 2026

Start and end datetimes used for structured data should be ISO-compatible and include the appropriate timezone.

## Registration and programme

The current registration workflow uses Google Forms and Google Sheets.

Registration is intended for ensembles and musicians who want to perform.

Relevant registration information may include:

- ensemble name
- contact person
- e-mail
- telephone
- musician names
- instruments
- composer
- piece
- estimated duration
- additional notes

The website should provide a clear registration route.

A provisional programme is intended to be published for the upcoming event. Submitted data should not automatically become public without an appropriate approval/status workflow.

The long-term architecture may automate:

    Google Form
        ↓
    Google Sheet
        ↓
    approved programme data
        ↓
    build process
        ↓
    website

Do not invent programme entries or publish unverified participant information.

## SEO and LLM discoverability

The website should be understandable and discoverable by search engines and AI/LLM systems.

Preserve:

- meaningful page titles
- meta description
- canonical URL
- Open Graph metadata
- semantic HTML
- Schema.org structured data
- event information as normal HTML text
- sitemap
- robots.txt

Important information must not exist only in JavaScript or visual elements.

When changing event information, check whether structured data, metadata or sitemap content also needs to change.

## GitHub and deployment

The production repository is:

    https://github.com/eckhardtubbens/kamercirkel

The production website is intended to be:

    https://kamercirkel.nl

The domain is registered separately and DNS is managed by the domain registrar.

The website itself is hosted by GitHub Pages.

GitHub Actions automatically builds and deploys the website.

Do not introduce separate web hosting, a backend server or a CMS unless the user explicitly requests it.

## Dependency philosophy

Keep the project lightweight.

Prefer the existing stack:

- Python
- Jinja2
- PyYAML
- HTML
- CSS
- Git
- GitHub Actions
- GitHub Pages
- Google Forms/Sheets where appropriate

Avoid introducing:

- React
- Vue
- large JavaScript frameworks
- WordPress
- databases
- backend servers
- unnecessary build systems

unless explicitly requested and justified.

## Testing workflow

Before considering a change complete:

1. Modify the relevant source files.
2. Run:

       python build.py

3. Check for build errors.
4. Inspect the generated website locally.
5. Test mobile layout when relevant.
6. Test links and dynamic content.
7. Run `git status`.
8. Commit the change.
9. Push to GitHub.
10. Verify GitHub Actions.
11. Verify the deployed website.

## Architectural discipline

Do not solve a simple content problem by changing the architecture.

For example, if an event date changes, prefer:

    site.yaml

rather than editing several HTML and Python files.

If a new visual treatment is requested, prefer:

    css/style.css

If a new HTML section is requested, prefer:

    templates/index.html

If data needs to be transformed or formatted, use:

    build.py

If deployment behaviour changes, use:

    .github/workflows/

## Documentation discipline

When the architecture changes:

1. update the implementation;
2. update `ARCHITECTURE.md`;
3. update these Copilot instructions if the change affects project-wide rules;
4. keep `README.md` concise and accurate.

Do not leave architectural decisions undocumented.

## Avoid assumptions

Do not assume that a feature is already automated simply because it is planned.

In particular:

- Google Form → Google Sheet → programme automation is a planned direction unless the repository contains an actual implementation.
- A provisional programme may currently be manually curated.
- Multiple-event support is a future direction unless implemented.
- Image uploads are a future direction unless implemented.

Inspect the repository before claiming that a feature exists.

## When proposing major changes

For architectural changes, first explain:

- what changes;
- why it is needed;
- which files are affected;
- whether new dependencies are required;
- whether GitHub Actions or DNS/deployment changes are required.

Prefer incremental changes that fit the existing architecture.

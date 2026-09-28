# Ticketverkoop instellen

De ticketflow gebruikt een Google Apps Script-webapp en een Google Sheet.
`ticket-events.json` is de centrale bron voor alle concerten, inclusief datum,
tijden, locatie, prijs en één bunq.me-basislink. `build.py` leest en valideert
dit bestand, maar overschrijft het niet. De webapp slaat de bestelling met
gekozen concert op en maakt de betaal-URL dynamisch op basis van het totaal.
Bijvoorbeeld: basis-URL `https://bunq.me/kamercirkel` plus totaal `20` wordt
`https://bunq.me/kamercirkel/20`. De betaalstatus wordt niet
automatisch door bunq teruggekoppeld; controleer de betaling in bunq en wijzig
daarna de status in de Sheet. Na klikken op **Afrekenen** wordt de order
opgeslagen en opent bunq direct in een nieuw tabblad. Als opslaan mislukt,
sluit dat tabblad en blijft de foutmelding bij het formulier staan.

Na het opslaan verstuurt Apps Script ook een bestelbevestiging met concert,
aantal kaartjes, totaalbedrag, ordernummer en betaallink. De mail vermeldt dat
de bestelling pas definitief is na betaling. Een mailfout blokkeert de bunq-
checkout niet.

Bij betaalde edities in de agenda toont de website ook een koopknop. Die knop
opent de ticketwebapp met de betreffende concertdatum vooraf geselecteerd.

## Eenmalig instellen

1. Maak een Google Sheet aan voor de ticketorders.
2. Maak via [Google Apps Script](https://script.google.com/) een nieuw project.
3. Voeg `Code.gs` en `TicketPage.html` uit deze map toe aan dat project.
4. Open **Projectinstellingen** en voeg deze script property toe:

   | Property | Waarde |
   | --- | --- |
   | `SPREADSHEET_ID` | ID uit de URL van de Google Sheet |

    De Sheet-ID blijft als enige property privé in Apps Script. Zet deze niet in
    `site.yaml` of `ticket-events.json`: dat JSON-bestand wordt openbaar
    gepubliceerd. De bunq-basislink staat centraal bovenaan
    `ticket-events.json`:

   ```json
    {
       "payment_base_url": "https://bunq.me/kamercirkel",
       "events": []
    }
   ```

    Beheer concerten in de `events`-lijst van `ticket-events.json` en stel daar
    per concert `price` in. Het formulier berekent het totaal als prijs maal
   aantal kaartjes en gebruikt dat bedrag achter de basislink. Stel ook
   `max_tickets_per_order` in; dat bepaalt de aantalselectie en wordt server-side
   gecontroleerd. Controleer dat je bunq.me-account dynamische bedraglinks met
   dit URL-patroon ondersteunt.

5. Deploy het project als **Web app**, kies **Execute as me** en stel toegang in
   op **Anyone**. Geef de Sheet niet publiek toegankelijk; alleen de webapp
   schrijft erin.
6. Kopieer de `/exec`-URL van de webapp naar `event.tickets.sales_url` in
   `site.yaml`. Stel `event.current_event_id` in op het ID van de editie die op
   de homepage moet staan. Voer `python build.py` uit en publiceer de site samen
   met `ticket-events.json`; het Apps Script haalt concerten, prijzen en
   bunq-links op via `https://kamercirkel.nl/ticket-events.json`.
7. Bij het eerste gebruik autoriseer je de Apps Script-toegang tot externe URL's
   wanneer Google daarom vraagt.
8. Selecteer in de Apps Script-editor `authorizeEmailSending` en klik **Run**.
   Autoriseer Gmail wanneer Google daarom vraagt. Dit stuurt een eenmalige
   testmail naar het account waaronder de webapp wordt uitgevoerd. Bevestigingen
   worden ook vanaf dat account verstuurd; antwoorden gaan naar
   `info@kamercirkel.nl`.

## Bestellingen controleren

De webapp maakt de tab `Ticketorders` aan en schrijft elke inzending weg met de
gekozen concertnaam en -datum en status `Nog te controleren`. Bij een bestaande
Sheet voegt de webapp de concertkolommen achter de bestaande kolommen toe.
Vergelijk de bunq-betaling met concert, naam en bedrag en zet de status in de
Sheet handmatig op `Betaald`. Gebruik voor de deur alleen bestellingen met die
status. Een terugkeer vanaf een bunq-betaallink is op zichzelf geen bewijs dat
er betaald is.

Beperk de toegang tot de Sheet tot de organisatoren en verwijder persoonsgegevens
wanneer ze niet meer nodig zijn.
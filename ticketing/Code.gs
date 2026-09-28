const ORDER_SHEET_NAME = "Ticketorders";
const ORDER_HEADERS = [
  "Aangemaakt",
  "Ordernummer",
  "Naam",
  "E-mail",
  "Aantal kaartjes",
  "Totaal (EUR)",
  "Betaalstatus",
  "Concert",
  "Concertdatum",
];

const TICKET_EVENTS_URL = "https://kamercirkel.nl/ticket-events.json";

function doGet(e) {
  getSettings_();
  const events = getTicketEvents_();
  const selectedEventId = e && e.parameter ? e.parameter.concert || "" : "";
  const template = HtmlService.createTemplateFromFile("TicketPage");

  template.settings = {
    events: events,
    eventsJson: JSON.stringify(events),
    selectedEventId: selectedEventId,
  };

  return template
    .evaluate()
    .setTitle("Kaartje kopen | Kamercirkel")
    .addMetaTag("viewport", "width=device-width, initial-scale=1");
}

function submitTicketOrder(form) {
  if (!form || typeof form !== "object") {
    throw new Error("Vul het formulier opnieuw in.");
  }

  if (String(form.website || "").trim()) {
    throw new Error("Deze bestelling kon niet worden verwerkt.");
  }

  const settings = getSettings_();
  const name = String(form.name || "").trim();
  const email = String(form.email || "").trim().toLowerCase();
  const quantity = Number(form.quantity);
  const selectedEventId = String(form.concert || "").trim();
  const selectedEvent = getTicketEvents_().find(function (ticketEvent) {
    return ticketEvent.id === selectedEventId;
  });

  if (!name || name.length > 120) {
    throw new Error("Vul je naam in (maximaal 120 tekens).");
  }

  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 254) {
    throw new Error("Vul een geldig e-mailadres in.");
  }

  if (!selectedEvent) {
    throw new Error("Kies een concert uit de lijst.");
  }

  if (
    !Number.isInteger(quantity) ||
    quantity <= 0 ||
    quantity > selectedEvent.max_tickets_per_order
  ) {
    throw new Error("Kies een geldig aantal kaartjes.");
  }

  const orderId = Utilities.getUuid().toUpperCase();
  const total = Math.round(selectedEvent.price * quantity * 100) / 100;
  const paymentUrl = selectedEvent.payment_base_url + "/" + formatPaymentAmount_(total);

  if (!isValidBunqUrl_(paymentUrl)) {
    throw new Error("De bunq-betaallink voor dit concert is ongeldig.");
  }
  const lock = LockService.getScriptLock();
  lock.waitLock(10000);

  try {
    const spreadsheet = SpreadsheetApp.openById(settings.spreadsheetId);
    let sheet = spreadsheet.getSheetByName(ORDER_SHEET_NAME);

    if (!sheet) {
      sheet = spreadsheet.insertSheet(ORDER_SHEET_NAME);
    }

    if (sheet.getLastRow() === 0) {
      sheet.getRange(1, 1, 1, ORDER_HEADERS.length).setValues([ORDER_HEADERS]);
    } else {
      const currentHeaders = sheet
        .getRange(1, 1, 1, sheet.getLastColumn())
        .getValues()[0];
      const missingHeaders = ORDER_HEADERS.filter(function (header) {
        return currentHeaders.indexOf(header) === -1;
      });

      if (missingHeaders.length > 0) {
        sheet
          .getRange(1, sheet.getLastColumn() + 1, 1, missingHeaders.length)
          .setValues([missingHeaders]);
      }
    }

    sheet.setFrozenRows(1);
    sheet.appendRow([
      new Date(),
      orderId,
      safeSheetText_(name),
      safeSheetText_(email),
      quantity,
      total,
      "Nog te controleren",
      selectedEvent.title,
      selectedEvent.date_label,
    ]);
  } finally {
    lock.releaseLock();
  }

  sendOrderConfirmation_(email, name, selectedEvent, quantity, total, orderId, paymentUrl);

  return {
    orderId: orderId,
    paymentUrl: paymentUrl,
    eventLabel: selectedEvent.label,
  };
}

function sendOrderConfirmation_(email, name, selectedEvent, quantity, total, orderId, paymentUrl) {
  try {
    const replyToAddress = "info@kamercirkel.nl";
    const options = {
      name: "Kamercirkel",
      replyTo: replyToAddress,
      htmlBody: [
        "<p>Beste " + escapeHtml_(name) + ",</p>",
        "<p>We hebben je bestelling ontvangen. Je kaartjes zijn pas definitief nadat de betaling is ontvangen.</p>",
        "<p><strong>Concert:</strong> " + escapeHtml_(selectedEvent.label) + "<br>",
        "<strong>Aantal kaartjes:</strong> " + quantity + "<br>",
        "<strong>Totaal:</strong> " + formatEmailAmount_(total) + "<br>",
        "<strong>Ordernummer:</strong> " + orderId + "</p>",
        '<p><a href="' + escapeHtml_(paymentUrl) + '">Rond je betaling af via bunq</a></p>',
        "<p>Met vriendelijke groet,<br>Kamercirkel</p>",
      ].join(""),
    };

    const plainBody = [
      "Beste " + name + ",",
      "",
      "We hebben je bestelling ontvangen. Je kaartjes zijn pas definitief nadat de betaling is ontvangen.",
      "Concert: " + selectedEvent.label,
      "Aantal kaartjes: " + quantity,
      "Totaal: " + formatEmailAmount_(total),
      "Ordernummer: " + orderId,
      "",
      "Rond je betaling af via bunq: " + paymentUrl,
      "",
      "Met vriendelijke groet,",
      "Kamercirkel",
    ].join("\n");

    GmailApp.sendEmail(
      email,
      "Bestelbevestiging kaartjes Kamercirkel",
      plainBody,
      options,
    );
  } catch (error) {
    console.error("Bestelling opgeslagen maar bevestigingsmail verzenden mislukte: " + error);
  }
}

function authorizeEmailSending() {
  const accountEmail = Session.getEffectiveUser().getEmail();

  if (!accountEmail) {
    throw new Error("Het uitvoerende Google-account kon niet worden bepaald.");
  }

  GmailApp.sendEmail(
    accountEmail,
    "Kamercirkel: e-mailtoestemming getest",
    "E-mailverzending voor ticketbevestigingen is geautoriseerd.",
    { name: "Kamercirkel", replyTo: "info@kamercirkel.nl" },
  );
}

function formatEmailAmount_(amount) {
  return "€" + (Number.isInteger(amount) ? amount : amount.toFixed(2));
}

function escapeHtml_(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function getTicketEvents_() {
  const response = UrlFetchApp.fetch(TICKET_EVENTS_URL, {
    muteHttpExceptions: true,
  });

  if (response.getResponseCode() !== 200) {
    throw new Error("De concertlijst van de website is tijdelijk niet bereikbaar.");
  }

  let eventData;
  try {
    eventData = JSON.parse(response.getContentText());
  } catch (error) {
    throw new Error("De concertlijst van de website is ongeldig.");
  }

  if (!eventData || !Array.isArray(eventData.events)) {
    throw new Error("De concertlijst van de website is ongeldig.");
  }

  if (!/^https:\/\/bunq\.me\/[a-z0-9_-]+$/i.test(eventData.payment_base_url || "")) {
    throw new Error("De dynamische bunq-betaallink is niet goed ingesteld.");
  }

  return eventData.events.filter(function (ticketEvent) {
    return (
      ticketEvent &&
      typeof ticketEvent.id === "string" &&
      typeof ticketEvent.title === "string" &&
      typeof ticketEvent.date === "string" &&
      typeof ticketEvent.price === "number" &&
      ticketEvent.price > 0 &&
      Number.isInteger(ticketEvent.max_tickets_per_order) &&
      ticketEvent.max_tickets_per_order > 0 &&
      ticketEvent.location &&
      typeof ticketEvent.location.name === "string"
    );
  }).map(function (ticketEvent) {
    const dateLabel = new Intl.DateTimeFormat("nl-NL", {
      day: "numeric",
      month: "long",
      year: "numeric",
      timeZone: "UTC",
    }).format(new Date(ticketEvent.date + "T12:00:00Z"));

    return Object.assign({}, ticketEvent, {
      date_label: dateLabel,
      label: dateLabel + " · " + ticketEvent.location.name,
      payment_base_url: eventData.payment_base_url,
    });
  });
}

function formatPaymentAmount_(amount) {
  return Number.isInteger(amount) ? String(amount) : amount.toFixed(2);
}

function isValidBunqUrl_(paymentUrl) {
  return (
    typeof paymentUrl === "string" &&
    /^https:\/\/(?:[a-z0-9-]+\.)*bunq\.(?:me|com)(?:[/?#]|$)/i.test(paymentUrl)
  );
}

function getSettings_() {
  const properties = PropertiesService.getScriptProperties();
  const spreadsheetId = properties.getProperty("SPREADSHEET_ID");

  if (!spreadsheetId) {
    throw new Error("De Sheet-ID is nog niet ingesteld in Script Properties.");
  }

  return { spreadsheetId: spreadsheetId };
}

function safeSheetText_(value) {
  return /^[\s]*[=+\-@]/.test(value) ? "'" + value : value;
}
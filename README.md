# seasonlab-data

Tagesschlusskurse für die Season-Lab-Seite. Eine GitHub Action lädt die Kurse jeden Werktag nach US-Börsenschluss und samstags, und speichert sie hier.

- `data/<ID>.csv`: Kurse je Instrument (Datum, Open, High, Low, Close), ab 1993 oder Handelsbeginn
- `site/index.json`: Liste aller Instrumente
- `site/<gruppe>.json`: kompakte Reihen für die Seite (forex, metalle, rohstoffe, indizes, krypto, aktien-us, aktien-eu)

Quelle: Yahoo Finance. Aktienkurse sind um Splits und Dividenden bereinigt. Metalle und Rohstoffe sind fortlaufende Front-Month-Futures.

Manuell starten: Tab **Actions** → **Kursdaten aktualisieren** → **Run workflow**.

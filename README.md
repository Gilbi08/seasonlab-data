# seasonlab-data

Tagesschlusskurse für die Season-Lab-Seite. Eine GitHub Action lädt die Kurse täglich um 02:25 UTC (nach Forex-, US- und Krypto-Tagesschluss) und speichert sie hier.

- `data/<ID>.csv`: Kurse je Instrument (Datum, Open, High, Low, Close), ab 1993 oder Handelsbeginn
- `site/index.json`: Liste aller Instrumente
- `site/<gruppe>.json`: kompakte Reihen für die Seite (forex, metalle, rohstoffe, indizes, krypto, aktien-us, aktien-eu)

Quelle: Yahoo Finance. Aktienkurse sind um Splits und Dividenden bereinigt. Metalle als Spotkurs, wenn Yahoo ihn liefert, sonst wie die Rohstoffe als fortlaufender Front-Month-Future.

Manuell starten: Tab **Actions** → **Kursdaten aktualisieren** → **Run workflow**.

Hinweis Devisen: Yahoo datiert Forex-Tageskerzen auf den Folgetag (Kurs um Mitternacht London). `fetch.py` ordnet sie deshalb dem vorherigen Handelstag zu. So liegen die Kurse im Schnitt nur etwa 0,1 % neben dem Broker-Tagesschluss (17 Uhr New York).

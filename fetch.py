#!/usr/bin/env python3
"""Season Lab – Kursdaten.

Lädt Tagesschlusskurse (Yahoo Finance) für alle Instrumente und schreibt
  data/<ID>.csv        lesbare CSV je Instrument (Date,Open,High,Low,Close)
  site/index.json      Liste aller Instrumente mit Metadaten
  site/<gruppe>.json   kompakte Kursreihen je Gruppe für die Season-Lab-Seite

Schlägt ein Download fehl, bleibt die vorhandene CSV erhalten.
"""
import datetime as dt
import json
import math
import os
import sys
import time

import pandas as pd
import yfinance as yf

START = "1993-01-01"
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(ROOT, "data")
SITE = os.path.join(ROOT, "site")

PAIRS = [
    "EURUSD", "GBPUSD", "AUDUSD", "NZDUSD", "USDJPY", "USDCHF", "USDCAD", "USDSEK", "USDNOK",
    "USDMXN", "USDZAR", "USDCNY", "USDSGD", "USDINR", "USDBRL", "USDTRY", "USDPLN", "USDHUF",
    "EURJPY", "EURGBP", "EURCHF", "EURAUD", "EURCAD", "EURNZD", "EURSEK", "EURNOK", "EURPLN",
    "GBPJPY", "GBPCHF", "GBPAUD", "GBPCAD", "GBPNZD", "AUDJPY", "AUDNZD", "AUDCAD", "AUDCHF",
    "CADJPY", "CADCHF", "CHFJPY", "NZDJPY", "NZDCAD", "NZDCHF",
]

# (ID, Name, Gruppe, Kategorie, Einheit, Yahoo-Ticker)
INSTR = [(p, f"{p[:3]}/{p[3:]}", "forex", "Forex", p[3:], f"{p}=X") for p in PAIRS]
INSTR += [
    ("XAUUSD", "Gold", "metalle", "Metalle", "USD/oz", ["XAUUSD=X", "GC=F"]),
    ("XAGUSD", "Silber", "metalle", "Metalle", "USD/oz", ["XAGUSD=X", "SI=F"]),
    ("XPTUSD", "Platin", "metalle", "Metalle", "USD/oz", ["XPTUSD=X", "PL=F"]),
    ("XPDUSD", "Palladium", "metalle", "Metalle", "USD/oz", ["XPDUSD=X", "PA=F"]),
    ("COPPER", "Kupfer", "metalle", "Metalle", "USD/lb", "HG=F"),
    ("WTI", "WTI-Rohöl", "rohstoffe", "Rohstoffe", "USD/bbl", "CL=F"),
    ("BRENT", "Brent-Rohöl", "rohstoffe", "Rohstoffe", "USD/bbl", "BZ=F"),
    ("NATGAS", "Erdgas", "rohstoffe", "Rohstoffe", "USD/MMBtu", "NG=F"),
    ("GASOLINE", "Benzin (RBOB)", "rohstoffe", "Rohstoffe", "USD/gal", "RB=F"),
    ("HEATOIL", "Heizöl", "rohstoffe", "Rohstoffe", "USD/gal", "HO=F"),
    ("WHEAT", "Weizen", "rohstoffe", "Rohstoffe", "USc/bu", "ZW=F"),
    ("CORN", "Mais", "rohstoffe", "Rohstoffe", "USc/bu", "ZC=F"),
    ("SOYBEAN", "Sojabohnen", "rohstoffe", "Rohstoffe", "USc/bu", "ZS=F"),
    ("COFFEE", "Kaffee", "rohstoffe", "Rohstoffe", "USc/lb", "KC=F"),
    ("SUGAR", "Zucker", "rohstoffe", "Rohstoffe", "USc/lb", "SB=F"),
    ("COCOA", "Kakao", "rohstoffe", "Rohstoffe", "USD/t", "CC=F"),
    ("COTTON", "Baumwolle", "rohstoffe", "Rohstoffe", "USc/lb", "CT=F"),
    ("CATTLE", "Lebendrind", "rohstoffe", "Rohstoffe", "USc/lb", "LE=F"),
    ("SPX", "S&P 500", "indizes", "Indizes", "Punkte", "^GSPC"),
    ("NDX", "Nasdaq 100", "indizes", "Indizes", "Punkte", "^NDX"),
    ("DJI", "Dow Jones", "indizes", "Indizes", "Punkte", "^DJI"),
    ("RUT", "Russell 2000", "indizes", "Indizes", "Punkte", "^RUT"),
    ("DAX", "DAX 40", "indizes", "Indizes", "Punkte", "^GDAXI"),
    ("ATX", "ATX", "indizes", "Indizes", "Punkte", "^ATX"),
    ("ESTX50", "Euro Stoxx 50", "indizes", "Indizes", "Punkte", "^STOXX50E"),
    ("FTSE", "FTSE 100", "indizes", "Indizes", "Punkte", "^FTSE"),
    ("CAC", "CAC 40", "indizes", "Indizes", "Punkte", "^FCHI"),
    ("SMI", "SMI", "indizes", "Indizes", "Punkte", "^SSMI"),
    ("N225", "Nikkei 225", "indizes", "Indizes", "Punkte", "^N225"),
    ("HSI", "Hang Seng", "indizes", "Indizes", "Punkte", "^HSI"),
    ("VIX", "VIX", "indizes", "Indizes", "Punkte", "^VIX"),
    ("DXY", "US-Dollar-Index", "indizes", "Indizes", "Punkte", "DX-Y.NYB"),
]
for c, n in [("BTC", "Bitcoin"), ("ETH", "Ethereum"), ("SOL", "Solana"), ("XRP", "XRP"), ("BNB", "BNB"),
             ("ADA", "Cardano"), ("DOGE", "Dogecoin"), ("LTC", "Litecoin"), ("LINK", "Chainlink"),
             ("DOT", "Polkadot"), ("AVAX", "Avalanche"), ("TRX", "Tron")]:
    INSTR.append((c + "USD", f"{n} ({c}/USD)", "krypto", "Krypto", "USD", f"{c}-USD"))
US = [("AAPL", "Apple"), ("MSFT", "Microsoft"), ("NVDA", "Nvidia"), ("AMZN", "Amazon"), ("GOOGL", "Alphabet"),
      ("META", "Meta"), ("TSLA", "Tesla"), ("AVGO", "Broadcom"), ("NFLX", "Netflix"), ("AMD", "AMD"),
      ("INTC", "Intel"), ("ORCL", "Oracle"), ("CRM", "Salesforce"), ("ADBE", "Adobe"), ("PLTR", "Palantir"),
      ("COIN", "Coinbase"), ("JPM", "JPMorgan"), ("V", "Visa"), ("MA", "Mastercard"), ("BRK-B", "Berkshire Hathaway"),
      ("WMT", "Walmart"), ("COST", "Costco"), ("KO", "Coca-Cola"), ("PEP", "PepsiCo"), ("MCD", "McDonald's"),
      ("NKE", "Nike"), ("DIS", "Disney"), ("XOM", "ExxonMobil"), ("JNJ", "Johnson & Johnson"), ("PG", "Procter & Gamble"),
      ("UNH", "UnitedHealth"), ("LLY", "Eli Lilly"), ("BA", "Boeing"), ("CAT", "Caterpillar"), ("SPY", "SPDR S&P 500 ETF"),
      ("QQQ", "Invesco QQQ ETF"), ("GLD", "SPDR Gold ETF")]
EU = [("SAP.DE", "SAP"), ("SIE.DE", "Siemens"), ("ALV.DE", "Allianz"), ("DTE.DE", "Deutsche Telekom"),
      ("MBG.DE", "Mercedes-Benz"), ("BMW.DE", "BMW"), ("VOW3.DE", "Volkswagen"), ("BAS.DE", "BASF"),
      ("ADS.DE", "Adidas"), ("RHM.DE", "Rheinmetall"), ("DBK.DE", "Deutsche Bank"), ("VOE.VI", "voestalpine"),
      ("OMV.VI", "OMV"), ("EBS.VI", "Erste Group"), ("VER.VI", "Verbund"), ("RBI.VI", "Raiffeisen Bank Intl."),
      ("ASML.AS", "ASML"), ("NESN.SW", "Nestlé"), ("NOVN.SW", "Novartis"), ("NOVO-B.CO", "Novo Nordisk"),
      ("MC.PA", "LVMH"), ("AIR.PA", "Airbus"), ("TTE.PA", "TotalEnergies"), ("SHEL.L", "Shell")]
for t, n in US:
    INSTR.append((t.replace("-", "").replace(".", ""), n, "aktien-us", "Aktien", "USD", t))
for t, n in EU:
    INSTR.append((t.replace("-", "").replace(".", ""), n, "aktien-eu", "Aktien", t.split(".")[-1], t))

CUR = {"DE": "EUR", "VI": "EUR", "AS": "EUR", "PA": "EUR", "SW": "CHF", "CO": "DKK", "L": "GBp"}


def download(ticker):
    for attempt in range(4):
        try:
            df = yf.download(ticker, start=START, interval="1d", auto_adjust=True,
                             progress=False, threads=False)
            if df is not None and len(df):
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = df.columns.get_level_values(0)
                return df
        except Exception as e:  # noqa
            print("  Fehler", ticker, e, file=sys.stderr)
        time.sleep(3 * (attempt + 1))
    return None


def prev_weekday(ts):
    d = ts - pd.Timedelta(days=1)
    while d.dayofweek >= 5:
        d -= pd.Timedelta(days=1)
    return d


def pick(tickers):
    """Erster Ticker mit langer, aktueller Historie."""
    fresh = pd.Timestamp.utcnow().tz_localize(None).normalize() - pd.Timedelta(days=10)
    for t in tickers:
        df = download(t)
        if df is not None and len(df) > 2000 and pd.to_datetime(df.index).tz_localize(None).max() >= fresh:
            return t, df
        print("  verworfen", t, 0 if df is None else len(df), file=sys.stderr)
    return tickers[-1], None


def clean(df, is_fx):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df[["Open", "High", "Low", "Close"]].copy()
    df = df[df["Close"] > 0].dropna(subset=["Close"])
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    df = df[~df.index.duplicated(keep="last")]
    today = pd.Timestamp.utcnow().tz_localize(None).normalize()
    if is_fx:
        # Yahoo datiert Devisen-Tageskerzen auf den Folgetag (Kurs um Mitternacht London).
        # Den Wert deshalb dem vorherigen Handelstag zuordnen, damit er zum Broker-Tagesschluss passt.
        df = df[df.index.dayofweek < 5]
        df.index = pd.DatetimeIndex([prev_weekday(d) for d in df.index])
        df = df[~df.index.duplicated(keep="last")]
    else:
        # angefangener Handelstag wird erst beim nächsten Lauf übernommen
        df = df[df.index < today]
    # einzelne Ausreißer (Sprung hin und sofort zurück) entfernen
    c = df["Close"]
    r1 = c / c.shift(1) - 1
    r2 = c.shift(-1) / c - 1
    lim = 0.08 if is_fx else 0.35
    bad = (r1.abs() > lim) & (r2.abs() > lim * 0.8) & (r1 * r2 < 0)
    return df[~bad]


def sig(x, n=7):
    return float(f"{x:.{n}g}")


def main():
    os.makedirs(DATA, exist_ok=True)
    os.makedirs(SITE, exist_ok=True)
    groups, index, failed = {}, [], []
    for sid, name, grp, cat, unit, ticker in INSTR:
        path = os.path.join(DATA, f"{sid}.csv")
        time.sleep(0.6)
        if isinstance(ticker, list):
            ticker, df = pick(ticker)
        else:
            df = download(ticker)
        if df is not None and len(df) > 200:
            df = clean(df, ticker.endswith("=X"))
            df.round(6).to_csv(path, index_label="Date")
            status = "neu"
        elif os.path.exists(path):  # Download fehlgeschlagen: letzte Daten behalten
            df = pd.read_csv(path, index_col="Date", parse_dates=True)
            status = "alt"
            failed.append(ticker)
        else:
            failed.append(ticker)
            print(f"{sid:10} {ticker:12} FEHLT")
            continue
        if grp == "aktien-eu":
            unit = CUR.get(ticker.split(".")[-1], unit)
        dates = [d.date() for d in df.index]
        closes = [float(x) for x in df["Close"]]
        pts = [(d, p) for d, p in zip(dates, closes) if p > 0 and math.isfinite(p)]
        start = pts[0][0]
        prev, dd, pp = start, [], []
        for d, p in pts:
            dd.append((d - prev).days)
            prev = d
            pp.append(sig(p))
        src = "Yahoo Finance (" + ticker + ")"
        if ticker.endswith("=F"):
            src += ", fortlaufender Front-Month-Future"
        if ticker.endswith("=X"):
            src += ", Tagesschluss vor Mitternacht London"
        groups.setdefault(grp, []).append({"id": sid, "start": start.isoformat(), "d": dd, "p": pp})
        index.append({"id": sid, "name": name, "grp": grp, "cat": cat, "unit": unit, "src": src,
                      "start": start.isoformat(), "end": pts[-1][0].isoformat(), "last": pp[-1], "n": len(pp)})
        print(f"{sid:10} {ticker:12} {status} {start} → {pts[-1][0]} {len(pp)}")
    for grp, ser in groups.items():
        with open(os.path.join(SITE, f"{grp}.json"), "w") as f:
            json.dump({"series": ser}, f, separators=(",", ":"))
    built = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    with open(os.path.join(SITE, "index.json"), "w") as f:
        json.dump({"built": built, "source": "Yahoo Finance, Tagesschlusskurse", "failed": failed,
                   "instruments": index}, f, ensure_ascii=False, separators=(",", ":"))
    print("fertig:", len(index), "Instrumente,", len(failed), "Fehler", failed)
    if len(index) < len(INSTR) * 0.8:
        sys.exit("Zu viele Downloads fehlgeschlagen")


if __name__ == "__main__":
    main()

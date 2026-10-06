#!/usr/bin/env python
"""
summarise_permit_register.py — reduce the private all-J&K stage-carriage permit
register to a table of COUNTS that is safe to keep in the repository.

The register has one row per permit, and each row carries a vehicle registration
number. Registration numbers are personal data (they identify an owner) and must
never enter this repository. This tool therefore reads the register from a path
given on the command line, uses the registration number only in memory to count
distinct vehicles, and writes aggregate counts only:

    data/raw/permit_register_summary.csv         counts, in blocks (see below)
    data/raw/permit_register_summary_meta.json   as-of date, definitions, input fingerprint

It writes no registration number, no owner or driver name, and no row-level data.
No cell is suppressed (small counts such as a 2-vehicle office are kept as they are,
because they are office-by-class aggregates and carry no identifying field).

Blocks in the CSV (column `block`):
    stock                         office x vehicle class x vehicle category x validity status
    validity_length               division flag x class x status x permit validity in whole
                                  years (Permit Upto minus Permit Valid From, rounded); rows
                                  whose end date is the placeholder get "placeholder"
    route_recorded_either_end     division flag x class x status x (origin OR destination
                                  location recorded: yes/no)
    route_recorded_both_ends      same, requiring both origin and destination

Validity status is evaluated on the register's latest permit date, as_of =
max(Permit Issue Date, Permit Valid From):
    valid        Permit Upto >= as_of
    expired      1990-01-01 <= Permit Upto < as_of
    placeholder  Permit Upto < 1990-01-01 (the register uses 1930-01-01 as a dummy end date)
    no_end_date  Permit Upto missing
Every count is given twice: `n_permit_rows` (rows of the register) and `n_vehicles`
(distinct registration numbers within the scope: Kashmir Division offices, or all other
offices; a vehicle with several permit rows in a scope is assigned the attributes of its
latest permit there, ordered by Permit Upto then Permit Valid From; a vehicle with permits
in both scopes is counted once in each, so n_vehicles over both scopes can exceed the
number of distinct vehicles in the register).

A valid permit is not proof that the bus operates.

Usage:
    python tools/summarise_permit_register.py "E:/kash/Mini Buses Routes in Srinagar.xlsx"
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "data" / "raw" / "permit_register_summary.csv"
PLACEHOLDER_BEFORE = pd.Timestamp("1990-01-01")

# The ten Kashmir Division transport offices (RTO / ARTO). Not named in the paper.
KASHMIR_OFFICES = (
    "SRINAGAR RTO", "BARAMULLA ARTO", "ANANTNAG ARTO", "PULWAMA ARTO", "GANDERBAL ARTO",
    "KULGAM ARTO", "KUPWARA ARTO", "BUDGAM ARTO", "BANDIPORA ARTO", "SHOPIAN ARTO",
)

REQUIRED = ["Office Name", "Registration No.", "Vehicle Category", "Vehicle Class",
            "Permit Issue Date", "Permit Valid From", "Permit Upto",
            "From Location", "To Location"]
COLUMNS = ["block", "in_kashmir_division", "office", "vehicle_class", "vehicle_category",
           "validity_status", "validity_years_rounded", "route_recorded",
           "n_permit_rows", "n_vehicles"]
ALL = "ALL"
REG_PATTERN = re.compile(r"JK\d{2}")


def load_register(path: Path) -> pd.DataFrame:
    df = pd.read_excel(path)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise SystemExit(f"register is missing expected columns: {missing}")
    for c in ("Permit Issue Date", "Permit Valid From", "Permit Upto"):
        df[c] = pd.to_datetime(df[c], errors="coerce")
    return df


def classify(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Timestamp]:
    as_of = max(df["Permit Issue Date"].max(), df["Permit Valid From"].max())
    out = df.copy()
    upto = out["Permit Upto"]
    out["validity_status"] = "expired"
    out.loc[upto >= as_of, "validity_status"] = "valid"
    out.loc[upto < PLACEHOLDER_BEFORE, "validity_status"] = "placeholder"
    out.loc[upto.isna(), "validity_status"] = "no_end_date"
    years = ((upto - out["Permit Valid From"]).dt.days / 365.25).round()
    out["validity_years_rounded"] = years.map(lambda y: "" if pd.isna(y) else str(int(y)))
    out.loc[out["validity_status"] == "placeholder", "validity_years_rounded"] = "placeholder"
    out.loc[out["validity_status"] == "no_end_date", "validity_years_rounded"] = "no_end_date"
    out["office"] = out["Office Name"].fillna("(blank)").astype(str)
    out["vehicle_class"] = out["Vehicle Class"].fillna("(blank)").astype(str)
    out["vehicle_category"] = out["Vehicle Category"].fillna("(blank)").astype(str)
    out["in_kashmir_division"] = out["office"].isin(KASHMIR_OFFICES)
    out["route_either"] = (out["From Location"].notna() | out["To Location"].notna())
    out["route_both"] = (out["From Location"].notna() & out["To Location"].notna())
    return out, as_of


def latest_per_vehicle(df: pd.DataFrame) -> pd.DataFrame:
    """One row per distinct registration number WITHIN its division scope (Kashmir
    Division offices / all other offices): its latest permit in that scope. A vehicle
    that holds permits in both scopes is therefore counted once in each."""
    d = df.copy()
    d["_ord"] = range(len(d))
    d = d.sort_values(["in_kashmir_division", "Registration No.", "Permit Upto",
                       "Permit Valid From", "_ord"], na_position="first")
    return d.drop_duplicates(["in_kashmir_division", "Registration No."], keep="last")


def count_block(rows: pd.DataFrame, veh: pd.DataFrame, block: str, keys: dict) -> pd.DataFrame:
    """Aggregate to counts over `keys` (dest column -> source column)."""
    src = list(keys.values())
    r = rows.groupby(src, dropna=False).size().rename("n_permit_rows")
    v = veh.groupby(src, dropna=False).size().rename("n_vehicles")
    t = pd.concat([r, v], axis=1).fillna(0).astype(int).reset_index()
    t = t.rename(columns={s: d for d, s in keys.items()})
    t.insert(0, "block", block)
    return t


def summarise(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    rows, as_of = classify(df)
    veh = latest_per_vehicle(rows)

    stock = count_block(rows, veh, "stock", dict(
        in_kashmir_division="in_kashmir_division", office="office", vehicle_class="vehicle_class",
        vehicle_category="vehicle_category", validity_status="validity_status"))

    length = count_block(rows, veh, "validity_length", dict(
        in_kashmir_division="in_kashmir_division", vehicle_class="vehicle_class",
        validity_status="validity_status", validity_years_rounded="validity_years_rounded"))

    def route_block(col: str, name: str) -> pd.DataFrame:
        r2, v2 = rows.copy(), veh.copy()
        for d in (r2, v2):
            d["route_recorded"] = d[col].map({True: "yes", False: "no"})
        return count_block(r2, v2, name, dict(
            in_kashmir_division="in_kashmir_division", vehicle_class="vehicle_class",
            validity_status="validity_status", route_recorded="route_recorded"))

    parts = [stock, length, route_block("route_either", "route_recorded_either_end"),
             route_block("route_both", "route_recorded_both_ends")]
    out = pd.concat(parts, ignore_index=True)
    for c in COLUMNS:
        if c not in out.columns:
            out[c] = ALL
    out = out[COLUMNS].fillna(ALL)
    out["in_kashmir_division"] = out["in_kashmir_division"].map(
        lambda x: ALL if x == ALL else ("yes" if x in (True, "True") else "no"))
    out = out.sort_values(COLUMNS[:8], kind="mergesort").reset_index(drop=True)

    meta = dict(
        as_of_date=str(as_of.date()),
        as_of_definition="max(Permit Issue Date, Permit Valid From) over the whole register",
        placeholder_end_date_before=str(PLACEHOLDER_BEFORE.date()),
        n_permit_rows=int(len(df)),
        n_distinct_vehicles=int(df["Registration No."].nunique()),
        kashmir_offices=list(KASHMIR_OFFICES),
        n_kashmir_offices_present=int(sum(o in set(rows["office"]) for o in KASHMIR_OFFICES)),
        status_definitions=dict(
            valid="Permit Upto >= as_of_date",
            expired="1990-01-01 <= Permit Upto < as_of_date",
            placeholder="Permit Upto before 1990-01-01 (dummy end date)",
            no_end_date="Permit Upto missing"),
        vehicle_rule=("n_vehicles counts distinct registration numbers within the division scope "
                      "(Kashmir Division offices / all other offices); a vehicle with several "
                      "permit rows in a scope takes the attributes of its latest permit there; a "
                      "vehicle with permits in both scopes is counted once in each"),
        route_recorded_definition=dict(
            either_end="From Location or To Location is non-blank on the permit row",
            both_ends="From Location and To Location are both non-blank"),
        caveat="A valid permit is not proof that the bus operates.",
        privacy=("counts only; no registration number, name or row-level record is written; "
                 "no cell suppressed"),
    )
    return out, meta


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("register", type=Path, help="path to the private permit register (.xlsx)")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args(argv)

    df = load_register(args.register)
    out, meta = summarise(df)
    meta["source_file_name"] = args.register.name
    h = hashlib.sha256()
    with args.register.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    meta["source_file_sha256"] = h.hexdigest()

    text = out.to_csv(index=False)
    if REG_PATTERN.search(text):
        raise SystemExit("refusing to write: output matches a registration-number pattern")
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(text, encoding="utf-8", newline="\n")
    meta_path = args.out.with_name(args.out.stem + "_meta.json")
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8",
                         newline="\n")
    print(f"wrote {args.out} ({len(out)} count rows) and {meta_path.name}; "
          f"as of {meta['as_of_date']}", file=sys.stderr)


if __name__ == "__main__":
    main()

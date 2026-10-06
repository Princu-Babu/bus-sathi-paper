"""Replace the 26 ArcGIS-sourced gazetteer points with OpenStreetMap-derived ones.

Offline. Reads the local Geofabrik extract (ODbL) and the gazetteer; never edits them.
Output: data/derived/gazetteer_osm_replacements.csv  (arcgis_* columns are PRIVATE,
publish=no; only osm_* columns may be redistributed).
Usage: .venv/Scripts/python.exe tools/regeocode_arcgis_points.py [--pbf PATH] [--rebuild]
"""
import argparse
import csv
import difflib
import json
import math
import re
import statistics
import sys
from collections import Counter
from pathlib import Path

import osmium
import pandas as pd
from shapely.geometry import Point, shape

ROOT = Path(__file__).resolve().parents[1]
BBOX = (73.7, 33.2, 75.7, 34.9)  # lon0, lat0, lon1, lat1
GAZ = Path("E:/kash/kashmir_gazetteer.csv")
PBF = Path("E:/kash/india-latest.osm.pbf")
DIST = ROOT / "data/raw/kashmir_districts_osm.geojson"
ROUTES = ROOT / "data/raw/Rationalised_Routes_Kashmir_v3.csv"
CACHE = ROOT / "audit/2026-10-02/_scratch/arcgis/osm_candidates.json"
OUT = ROOT / "data/derived/gazetteer_osm_replacements.csv"
NAME_KEYS = ["name", "name:en", "alt_name", "old_name", "official_name", "int_name"]
PLACES = {"city", "town", "village", "hamlet", "suburb", "neighbourhood", "locality"}
RANK = {"city": 0, "town": 0, "village": 1, "suburb": 2, "neighbourhood": 2,
        "hamlet": 3, "locality": 4, "bus_station": 2, "station": 3, "bus_stop": 5}


def inbox(lon, lat):
    return BBOX[0] <= lon <= BBOX[2] and BBOX[1] <= lat <= BBOX[3]


def kind(tags):
    p = tags.get("place")
    if p in PLACES:
        return p
    if tags.get("amenity") == "bus_station":
        return "bus_station"
    if tags.get("railway") == "station":
        return "station"
    if tags.get("highway") == "bus_stop":
        return "bus_stop"
    return None


def names_of(tags):
    return sorted({tags[k].strip() for k in NAME_KEYS if tags.get(k, "").strip()})


def build_cache(pbf):
    cands, wayrefs = [], {}
    fp = osmium.FileProcessor(pbf, osmium.osm.NODE).with_filter(
        osmium.filter.KeyFilter("place", "amenity", "railway", "highway"))
    for n in fp:
        k = kind(n.tags)
        nm = names_of(n.tags) if k else []
        if k and nm and n.location.valid() and inbox(n.location.lon, n.location.lat):
            cands.append(dict(t="node", id=n.id, lat=n.location.lat, lon=n.location.lon, k=k, names=nm))
    fp = osmium.FileProcessor(pbf, osmium.osm.WAY).with_filter(
        osmium.filter.KeyFilter("place", "amenity", "railway"))
    for w in fp:
        k = kind(w.tags)
        nm = names_of(w.tags) if k else []
        if k and nm:
            wayrefs[w.id] = ([n.ref for n in w.nodes], k, nm)
    need = {r for refs, _, _ in wayrefs.values() for r in refs}
    loc = {}
    fp = osmium.FileProcessor(pbf, osmium.osm.NODE).with_filter(osmium.filter.IdFilter(need))
    for n in fp:
        loc[n.id] = (n.location.lat, n.location.lon)
    for wid, (refs, k, nm) in wayrefs.items():
        pts = [loc[r] for r in refs if r in loc]
        if not pts:
            continue
        lat = sum(p[0] for p in pts) / len(pts)
        lon = sum(p[1] for p in pts) / len(pts)
        if inbox(lon, lat):
            cands.append(dict(t="way", id=wid, lat=lat, lon=lon, k=k, names=nm))
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    CACHE.write_text(json.dumps(cands))
    return cands


def raw_norm(s):
    return re.sub(r"[^A-Z0-9]", "", s.upper())


def canon(s):
    s = re.sub(r"[^A-Z0-9 ]", "", s.upper().replace("-", " "))
    s = re.sub(r"\s+", "", s)
    s = s.replace("OO", "U").replace("EE", "I").replace("OU", "U")
    s = re.sub(r"(POORA|PORA|PURA)$", "PUR", s)
    s = re.sub(r"(GAM|GUND)$", "G", s)
    s = s.replace("W", "V").replace("SH", "S").replace("KH", "K").replace("TH", "T")
    s = re.sub(r"(.)\1+", r"\1", s)
    return s


def hav(a, b, c, d):
    p = math.pi / 180
    x = math.sin((c - a) * p / 2) ** 2 + math.cos(a * p) * math.cos(c * p) * math.sin((d - b) * p / 2) ** 2
    return 2 * 6371008.8 * math.asin(math.sqrt(x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pbf", default=str(PBF))
    ap.add_argument("--rebuild", action="store_true")
    a = ap.parse_args()
    cands = json.loads(CACHE.read_text()) if CACHE.exists() and not a.rebuild else build_cache(a.pbf)
    print(f"{len(cands)} OSM candidate objects", file=sys.stderr)

    polys = {f["properties"]["district"]: shape(f["geometry"])
             for f in json.load(open(DIST))["features"]}

    def district_of(lat, lon):
        p = Point(lon, lat)
        for d, g in polys.items():
            if g.contains(p):
                return d
        return ""

    idx = []
    for c in cands:
        c["district"] = district_of(c["lat"], c["lon"])
        for nm in c["names"]:
            idx.append((c, nm, raw_norm(nm), canon(nm)))

    rows = [r for r in csv.DictReader(open(GAZ, encoding="utf-8")) if "arcgis" in r["source"]]
    out = []
    for r in rows:
        name, dist = r["name"], r["district"]
        alat, alon = float(r["lat"]), float(r["lon"])
        rn, cn = raw_norm(name), canon(name)
        matches = []
        for c, nm, rr, cc in idx:
            if rr == rn:
                matches.append((c, nm, "exact", 1.0))
            elif cc == cn:
                matches.append((c, nm, "variant", 0.97))
            else:
                sm = difflib.SequenceMatcher(None, cn, cc)
                if sm.real_quick_ratio() >= 0.85 and sm.quick_ratio() >= 0.85:
                    ratio = sm.ratio()
                    if ratio >= 0.85:
                        matches.append((c, nm, f"fuzzy:{ratio:.2f}", ratio))
        best = {}
        for m in matches:
            key = (m[0]["t"], m[0]["id"])
            if key not in best or m[3] > best[key][3]:
                best[key] = m
        ms = list(best.values())
        dd = {}
        for m in ms:
            dd[(m[0]["t"], m[0]["id"])] = hav(alat, alon, m[0]["lat"], m[0]["lon"])

        def sk(m):
            c = m[0]
            return (c["district"] != dist, -round(m[3], 2), RANK[c["k"]], dd[(c["t"], c["id"])])
        ms.sort(key=sk)
        row = dict(name=name, district=dist, arcgis_lat=alat, arcgis_lon=alon, publish="no",
                   osm_lat="", osm_lon="", osm_type="", osm_id="", osm_name_matched="",
                   osm_place_tag="", match_method="", n_candidates=len(ms),
                   in_recorded_district="", shift_m="", status="not_found", note="")
        if not ms:
            hints = {}
            for c, nm, rr, cc in idx:
                if c["district"] != dist or c["k"] not in PLACES:
                    continue
                rt = difflib.SequenceMatcher(None, cn, cc).ratio()
                if rt >= 0.68:
                    hints[(c["t"], c["id"])] = (rt, f"{nm}[{c['k']}] {c['t']}/{c['id']} {c['lat']:.4f},{c['lon']:.4f} "
                                                f"r={rt:.2f} {hav(alat, alon, c['lat'], c['lon']) / 1000:.1f}km")
            top = [v[1] for v in sorted(hints.values(), reverse=True)[:3]]
            row["note"] = "no OSM name match >=0.85" + (
                "; near-misses in district, below threshold, NOT used (human review): " + " | ".join(top) if top else "")
            out.append(row)
            continue
        b = ms[0]
        c = b[0]
        d0 = dd[(c["t"], c["id"])]
        indist = c["district"] == dist
        tier = [m for m in ms if (m[0]["district"] == dist) == indist
                and round(m[3], 2) == round(b[3], 2) and RANK[m[0]["k"]] == RANK[c["k"]]]
        far = [m for m in tier[1:] if hav(c["lat"], c["lon"], m[0]["lat"], m[0]["lon"]) > 2000]
        notes, status = [], "replaced"
        if far:
            status = "ambiguous"
            notes.append("tied candidates >2 km apart")
        if b[2].startswith("fuzzy") and b[3] < 0.92:
            status = "ambiguous"
            notes.append("fuzzy match <0.92")
        if not indist:
            status = "ambiguous"
            notes.append(f"best OSM point is in '{c['district'] or 'outside 10 districts'}', not {dist}")
        alts = [f"{m[1]}[{m[0]['k']},{m[0]['district'] or '-'}] {m[0]['t']}/{m[0]['id']} "
                f"{m[0]['lat']:.4f},{m[0]['lon']:.4f} {m[2]}" for m in ms[1:6]]
        if alts:
            notes.append("alts: " + " | ".join(alts))
        row.update(osm_lat=round(c["lat"], 6), osm_lon=round(c["lon"], 6), osm_type=c["t"],
                   osm_id=c["id"], osm_name_matched=b[1], osm_place_tag=c["k"], match_method=b[2],
                   in_recorded_district=str(indist).lower(), shift_m=round(d0), status=status,
                   note="; ".join(notes))
        out.append(row)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    # route usage: active = Action_Taken != MERGED_INTO_TRUNK (186 routes)
    d = pd.read_csv(ROUTES)
    d = d[d.Action_Taken != "MERGED_INTO_TRUNK"]
    use = {}
    for o in out:
        rx = re.compile(r"(?<![A-Z0-9])" + re.escape(o["name"]) + r"(?![A-Z0-9])")
        use[o["name"]] = [rid for rid, rn in zip(d.Route_ID, d.Route_Name)
                          if rx.search(re.sub(r"[^A-Z0-9]+", " ", str(rn).upper()).strip())]
        if not use[o["name"]]:
            k = raw_norm(o["name"])
            use[o["name"]] = [rid for rid, rn in zip(d.Route_ID, d.Route_Name) if k in raw_norm(str(rn))]
    json.dump(use, open(CACHE.parent / "route_usage.json", "w"), indent=1)
    sh = [o["shift_m"] for o in out if o["shift_m"] != ""]
    print(Counter(o["status"] for o in out), "median", statistics.median(sh) if sh else None,
          "max", max(sh) if sh else None)
    print("active routes touching:", len(set(r for v in use.values() for r in v)), "of", len(d))


if __name__ == "__main__":
    main()

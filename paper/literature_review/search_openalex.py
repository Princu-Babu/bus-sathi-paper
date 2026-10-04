"""Reproducible OpenAlex search for §2 literature review.
Run: python search_openalex.py  -> raw_results.csv, search_log.csv
"""
import csv, datetime, json, time, urllib.error, urllib.parse, urllib.request

BASE = "https://api.openalex.org/works"
FILTER = "publication_year:2000-2026,type:article|proceedings-article|review,language:en"
PER_QUERY = 5000  # retrieve all hits (no relevance cap)

BUS = '(bus OR "public transport" OR transit)'
QUERIES = {
    # core A AND B
    "A_core_design": f'("transit network design" OR "bus network design" OR "route network design") AND {BUS}',
    "A_rationalisation": f'("route rationalisation" OR "route rationalization" OR "network redesign" OR "route restructuring") AND {BUS}',
    "A_freq_fleet": f'("frequency setting" OR "headway" OR "fleet size" OR "fleet sizing") AND ("bus route" OR "transit route" OR "bus network")',
    "AB_demand_data": f'("transit network design" OR "bus route design" OR "frequency setting") AND ("origin-destination" OR "smart card" OR "automated fare collection" OR "passenger count")',
    "B_od_estimation": f'("origin-destination" OR "OD matrix") AND ("smart card" OR "fare collection" OR "passenger count" OR "GPS") AND {BUS}',
    "B_data_scarce": f'("data scarcity" OR "data-scarce" OR "limited data" OR "data-poor" OR "without demand data" OR "lack of data") AND {BUS} AND (planning OR network OR route)',
    "B_open_data": f'(OpenStreetMap OR "open data" OR "gridded population" OR WorldPop OR GTFS) AND {BUS} AND (network OR route OR accessibility OR coverage)',
    "B_accessibility": f'("accessibility" OR "coverage") AND ("bus network design" OR "transit network design" OR "bus route" OR "route planning")',
    "B_demand_proxy": f'("demand proxy" OR "demand index" OR "land use" OR "points of interest" OR "population density") AND ("bus route" OR "transit route" OR "bus network") AND (design OR planning OR rationalisation OR rationalization)',
    "B_equity": f'(equity OR "Gini" OR "Lorenz" OR "social exclusion" OR "transit desert") AND ("bus network" OR "transit network" OR "public transport network") AND (design OR planning OR accessibility)',
    "C_india": f'(India OR Indian) AND ("bus route" OR "bus network" OR "bus service" OR "public transport") AND (rationalisation OR rationalization OR design OR planning OR optimisation OR optimization)',
    "C_global_south": f'("Global South" OR "developing countries" OR "developing cities" OR paratransit OR "informal transport" OR minibus OR matatu OR "trotro" OR "jeepney") AND {BUS} AND ("route" OR "network") AND (planning OR design OR rationalisation OR rationalization OR mapping OR reform)',
    "C_permit_regulation": f'("route permit" OR "stage carriage" OR "bus regulation" OR "bus reform" OR "bus franchising" OR "gross cost contract") AND {BUS}',
}


def reconstruct(inv):
    if not inv:
        return ""
    pos = {}
    for word, idxs in inv.items():
        for i in idxs:
            pos[i] = word
    return " ".join(pos[i] for i in sorted(pos))


def fetch(query, tag):
    import os
    os.makedirs("cache", exist_ok=True)
    cp = os.path.join("cache", tag + ".json")
    if os.path.exists(cp):
        with open(cp, encoding="utf-8") as f:
            c = json.load(f)
        return c["total"], c["results"]
    out, cursor = [], "*"
    while len(out) < PER_QUERY and cursor:
        params = {"filter": FILTER + ",title_and_abstract.search:" + query, "per-page": 200, "cursor": cursor,
                  "select": "id,doi,display_name,publication_year,primary_location,cited_by_count,abstract_inverted_index,type,authorships"}
        url = BASE + "?" + urllib.parse.urlencode(params)
        for attempt in range(5):
            try:
                with urllib.request.urlopen(url, timeout=60) as r:
                    d = json.load(r)
                break
            except urllib.error.HTTPError as e:
                if attempt == 4:
                    raise
                time.sleep(20 * (attempt + 1))
        total = d["meta"]["count"]
        out.extend(d["results"])
        cursor = d["meta"].get("next_cursor")
        time.sleep(4)
    with open(cp, "w", encoding="utf-8") as f:
        json.dump({"query": query, "total": total, "results": out[:PER_QUERY]}, f)
    return total, out[:PER_QUERY]


def main():
    rows, log = {}, []
    for tag, q in QUERIES.items():
        total, res = fetch(q, tag)
        log.append({"tag": tag, "query": q, "filter": FILTER, "total_hits": total,
                    "retrieved": len(res), "run_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")})
        print(f"{tag:22s} hits={total:6d} kept={len(res)}")
        for w in res:
            key = (w.get("doi") or w["id"]).lower()
            if key in rows:
                rows[key]["queries"] += ";" + tag
                continue
            loc = w.get("primary_location") or {}
            src = (loc.get("source") or {}).get("display_name", "")
            auths = [a["author"]["display_name"] for a in (w.get("authorships") or [])][:4]
            rows[key] = {"openalex_id": w["id"], "doi": w.get("doi") or "", "year": w.get("publication_year"),
                         "title": w.get("display_name") or "", "authors": "; ".join(auths), "venue": src,
                         "type": w.get("type"), "cited_by": w.get("cited_by_count", 0),
                         "abstract": reconstruct(w.get("abstract_inverted_index")), "queries": tag}
    with open("raw_results.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(next(iter(rows.values())).keys()))
        wr.writeheader(); wr.writerows(rows.values())
    with open("search_log.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(log[0].keys()))
        wr.writeheader(); wr.writerows(log)
    print("unique records after DOI de-dup:", len(rows))


if __name__ == "__main__":
    main()

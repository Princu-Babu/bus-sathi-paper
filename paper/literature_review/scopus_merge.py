"""Merge Scopus export with OpenAlex corpus; apply identical keyword pre-filter to Scopus-only records."""
import pandas as pd, re
s = pd.read_csv("scopus_export_2026-10-01_abstracts.csv")
oa = pd.read_csv("raw_results.csv")
norm = lambda x: re.sub(r"[^a-z0-9]", "", str(x).lower())[:60]
oad = set(re.sub(r"^https?://doi.org/", "", x).lower() for x in oa.doi.dropna())
oat = set(norm(t) for t in oa.title.dropna())
s["in_openalex"] = s.DOI.str.lower().isin(oad) | s.Title.map(norm).isin(oat)
new = s[~s.in_openalex].copy()
t = (new.Title.fillna("") + " " + new.Abstract.fillna("") + " " + new["Author Keywords"].fillna("")).str.lower()
core = r"\b(?:bus|buses|public transport|public transit|transit network|transit route|minibus|paratransit|matatu|jeepney)\b"
topic = r"(?:route|network design|frequenc|headway|fleet|rationali|accessib|coverage|stop|origin-destination|od matri|demand|planning|redesign)"
off = r"(?:charging station|charging infrastructure|battery|crew scheduling|driver scheduling|vehicle scheduling problem|school bus|bus bar|busbar|data bus|can bus|fieldbus|power system|microgrid|autonomous shuttle|epidemi|covid|noise|air pollution exposure|emission inventory|freight|logistics|airport|aircraft|ship|vessel|metro station design|railway timetabl)"
new["reason"] = ""
new.loc[~t.str.contains(core), "reason"] = "no bus/public-transport term"
new.loc[t.str.contains(core) & ~t.str.contains(topic), "reason"] = "no planning/network term"
new.loc[t.str.contains(core) & t.str.contains(topic) & t.str.contains(off), "reason"] = "off-topic keyword"
keep = new[new.reason == ""].copy()
keep["sid"] = ["P%04d" % i for i in range(1, len(keep) + 1)]
keep.to_csv("scopus_to_screen.csv", index=False)
new[["EID", "DOI", "Title", "reason"]].to_csv("scopus_prefilter_log.csv", index=False)
print("scopus", len(s), "| overlap w/ OpenAlex", int(s.in_openalex.sum()), "| scopus-only", len(new))
print(new.reason.replace("", "KEEP").value_counts().to_string())
step = -(-len(keep) // 3)
for k in range(3):
    part = keep.iloc[k*step:(k+1)*step]
    with open(f"screening/scopus_batch_{k+1}.txt", "w", encoding="utf-8") as f:
        for _, r in part.iterrows():
            f.write(f"### {r.sid} | {r.Year} | {r['Source title']} | cites={r['Cited by']}\nTITLE: {r.Title}\nABSTRACT: {str(r.Abstract)[:700]}\n\n")
    print("batch", k+1, len(part))

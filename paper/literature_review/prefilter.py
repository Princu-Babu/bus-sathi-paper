"""Transparent keyword pre-filter before title/abstract screening. Logged in prefilter_log.csv."""
import pandas as pd, re
df = pd.read_csv("raw_results.csv")
t = (df.title.fillna("") + " " + df.abstract.fillna("")).str.lower()
core = r"\b(bus|buses|public transport|public transit|transit network|transit route|minibus|paratransit|matatu|jeepney)\b"
topic = r"(route|network design|frequenc|headway|fleet|rationali|accessib|coverage|stop|origin-destination|od matri|demand|planning|redesign)"
offtopic = r"(charging station|charging infrastructure|battery|crew scheduling|driver scheduling|vehicle scheduling problem|school bus|bus bar|busbar|data bus|can bus|fieldbus|power system|microgrid|autonomous shuttle|epidemi|covid|noise|air pollution exposure|emission inventory|freight|logistics|airport|aircraft|ship|vessel|metro station design|railway timetabl)"
df["r_core"] = t.str.contains(core)
df["r_topic"] = t.str.contains(topic)
df["r_off"] = t.str.contains(offtopic)
df["no_abstract"] = df.abstract.isna() | (df.abstract.fillna("").str.len() < 50)
df["reason"] = ""
df.loc[~df.r_core, "reason"] = "no bus/public-transport term"
df.loc[df.r_core & ~df.r_topic, "reason"] = "no planning/network term"
df.loc[df.r_core & df.r_topic & df.r_off, "reason"] = "off-topic keyword"
keep = df[df.reason == ""].copy()
df[["openalex_id","doi","title","reason"]].to_csv("prefilter_log.csv", index=False)
keep.drop(columns=["r_core","r_topic","r_off"]).sort_values("cited_by", ascending=False).to_csv("to_screen.csv", index=False)
print(df.reason.replace("", "KEEP").value_counts().to_string()); print("to screen:", len(keep), "| of which no abstract:", keep.no_abstract.sum())

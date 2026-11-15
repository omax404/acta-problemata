#!/usr/bin/env python3
"""Automated scraper & ingest pipeline for open science & industrial databases:
- HAL Open Archive API (hal.science)
- Theses.fr API
- Direct bibliographic extraction to bank/*.json format
"""
import urllib.request
import urllib.parse
import json
import pathlib
import sys

HAL_API = "https://api.archives-ouvertes.fr/search/"

def search_hal(query="\"génie industriel\" AND (\"maintenance\" OR \"ordonnancement\")", rows=10):
    """Query HAL Open Archive API for full-text industrial theses and papers."""
    params = {
        "q": query,
        "wt": "json",
        "fl": "docid,title_s,abstract_s,uri_s,files_s,producedDateY_i,authFullName_s",
        "rows": rows,
        "sort": "producedDateY_i desc"
    }
    url = f"{HAL_API}?{urllib.parse.urlencode(params)}"
    print(f"[HAL] Querying: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "ActaProblemataBot/1.0"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    
    docs = data.get("response", {}).get("docs", [])
    print(f"[HAL] Found {len(docs)} documents.")
    return docs

def format_as_candidate(doc):
    """Format HAL document into an Acta Problemata candidate sheet skeleton."""
    title = doc.get("title_s", ["Sans titre"])[0]
    uri = doc.get("uri_s", "")
    year = doc.get("producedDateY_i", "n.d.")
    authors = ", ".join(doc.get("authFullName_s", ["Auteur inconnu"]))
    abstract = doc.get("abstract_s", ["Aucun résumé disponible."])[0]
    
    return {
        "title": title,
        "source_url": uri,
        "source_publisher": f"HAL Open Archive, {year}",
        "authors": authors,
        "abstract": abstract[:400] + "..." if len(abstract) > 400 else abstract
    }

def main():
    q = sys.argv[1] if len(sys.argv) > 1 else "\"génie industriel\" Maroc"
    docs = search_hal(q, rows=5)
    for i, d in enumerate(docs, 1):
        c = format_as_candidate(d)
        print(f"\n--- Candidat #{i} ---")
        print(f"Titre   : {c['title']}")
        print(f"Lien    : {c['source_url']}")
        print(f"Auteurs : {c['authors']}")
        print(f"Extrait : {c['abstract']}\n")

if __name__ == "__main__":
    main()

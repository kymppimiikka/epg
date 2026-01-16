#!/usr/bin/env python3
import gzip
import urllib.request
import xml.etree.ElementTree as ET
import os

URLS = [
    "https://url.myepg.top/Kymppimiikka01",
    "https://url.myepg.top/hyDfJp",
]

os.makedirs("docs", exist_ok=True)

def fetch_xml(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = r.read()
    if data[:2] == b"\x1f\x8b":
        return gzip.decompress(data)
    return data

def prog_key(p: ET.Element) -> str:
    title = (p.findtext("title") or "").strip()
    return f"{p.get('channel','')}|{p.get('start','')}|{p.get('stop','')}|{title}"

channels = {}
programmes = {}

out_root = ET.Element("tv")

for url in URLS:
    xml = fetch_xml(url)
    root = ET.fromstring(xml)

    for ch in root.findall("channel"):
        cid = ch.get("id")
        if cid and cid not in channels:
            channels[cid] = ch

    for p in root.findall("programme"):
        k = prog_key(p)
        if k not in programmes:
            programmes[k] = p

for cid in sorted(channels):
    out_root.append(channels[cid])

for p in sorted(programmes.values(), key=lambda x: (x.get("channel",""), x.get("start",""))):
    out_root.append(p)

xml_out = ET.tostring(out_root, encoding="utf-8", xml_declaration=True)

with open("docs/merged.xml", "wb") as f:
    f.write(xml_out)

with gzip.open("docs/merged.xml.gz", "wb", compresslevel=9) as gz:
    gz.write(xml_out)

print("Merged EPG written")

#!/usr/bin/env python3
"""Validate the JSON/JSONL source data for Music Atlas (standard library only)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "data" / "atlas"
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
COUNTRY_RE = re.compile(r"^[A-Z]{2}$")
RELATIONS = {
    "associated_with", "influenced_by", "member_of", "performed_in",
    "based_in", "born_in", "recorded_in", "released_in_era",
    "uses_technique", "explores_concept",
}
CATEGORIES = {"genre", "practice", "technique", "philosophy", "scene", "sound"}
PLACE_KINDS = {"country", "region", "city", "scene", "venue"}
PRECISIONS = {"exact", "approximate", "unknown"}


class Validator:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.ids: dict[str, set[str]] = {
            "artist": set(), "place": set(), "era": set(),
            "concept": set(), "work": set(),
        }

    def error(self, where: str, message: str) -> None:
        self.errors.append(f"{where}: {message}")

    def load_json(self, filename: str, key: str) -> list[dict]:
        path = ATLAS / filename
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            self.error(filename, "file is missing")
            return []
        except (UnicodeError, json.JSONDecodeError) as exc:
            self.error(filename, f"invalid UTF-8 JSON: {exc}")
            return []
        if not isinstance(obj, dict):
            self.error(filename, "top-level value must be an object")
            return []
        if obj.get("schema_version") != "1.0.0":
            self.error(filename, 'schema_version must be "1.0.0"')
        rows = obj.get(key)
        if not isinstance(rows, list):
            self.error(filename, f'"{key}" must be an array')
            return []
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                self.error(f"{filename}[{index}]", "item must be an object")
        return [r for r in rows if isinstance(r, dict)]

    def add_id(self, kind: str, value: object, where: str) -> None:
        if not isinstance(value, str) or not ID_RE.fullmatch(value):
            self.error(where, "id must be lowercase kebab-case")
            return
        if value in self.ids[kind]:
            self.error(where, f"duplicate {kind} id: {value}")
        self.ids[kind].add(value)

    def strings(self, value: object, where: str) -> list[str]:
        if not isinstance(value, list) or any(not isinstance(x, str) for x in value):
            self.error(where, "must be an array of strings")
            return []
        return value

    def urls(self, value: object, where: str) -> None:
        for url in self.strings(value, where):
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or not parsed.netloc:
                self.error(where, f"invalid HTTP(S) URL: {url}")

    def year(self, value: object, where: str, nullable: bool = False) -> bool:
        if nullable and value is None:
            return True
        if isinstance(value, bool) or not isinstance(value, int):
            self.error(where, "must be an integer" + (" or null" if nullable else ""))
            return False
        if not 1 <= value <= 9999:
            self.error(where, "year must be between 1 and 9999")
            return False
        return True

    def run(self) -> int:
        # Artist IDs are inherited from the two existing catalogues.
        for filename in ("data/artists.json", "japan/artists.json"):
            path = ROOT / filename
            try:
                obj = json.loads(path.read_text(encoding="utf-8"))
                artists = obj["artists"]
                if not isinstance(artists, list):
                    raise ValueError('"artists" must be an array')
                for i, artist in enumerate(artists):
                    if not isinstance(artist, dict):
                        self.error(filename, f"artists[{i}] must be an object")
                    else:
                        self.add_id("artist", artist.get("id"), f"{filename}:artists[{i}]")
            except (OSError, UnicodeError, json.JSONDecodeError, KeyError, ValueError) as exc:
                self.error(filename, f"cannot load artist catalogue: {exc}")

        places = self.load_json("places.json", "places")
        for i, row in enumerate(places):
            w = f"places.json[{i}]"
            self.add_id("place", row.get("id"), w)
            for field in ("name", "kind"):
                if not isinstance(row.get(field), str) or not row[field].strip():
                    self.error(w, f"{field} is required and must be a non-empty string")
            if row.get("kind") not in PLACE_KINDS:
                self.error(w, f"kind must be one of {sorted(PLACE_KINDS)}")
            code = row.get("country_code")
            if code is not None and (not isinstance(code, str) or not COUNTRY_RE.fullmatch(code)):
                self.error(w, "country_code must be an ISO-style two-letter uppercase code or null")
            lat, lon = row.get("latitude"), row.get("longitude")
            if (lat is None) != (lon is None):
                self.error(w, "latitude and longitude must both be numbers or both be null")
            for field, value, low, high in (
                ("latitude", lat, -90, 90), ("longitude", lon, -180, 180)
            ):
                if value is not None and (
                    isinstance(value, bool) or not isinstance(value, (int, float)) or not low <= value <= high
                ):
                    self.error(w, f"{field} must be between {low} and {high}, or null")
            if row.get("precision") not in PRECISIONS:
                self.error(w, f"precision must be one of {sorted(PRECISIONS)}")
            self.urls(row.get("sources", []), f"{w}.sources")

        eras = self.load_json("eras.json", "eras")
        for i, row in enumerate(eras):
            w = f"eras.json[{i}]"
            self.add_id("era", row.get("id"), w)
            for field in ("label", "description"):
                if not isinstance(row.get(field), str):
                    self.error(w, f"{field} must be a string")
            start_ok = self.year(row.get("start_year"), f"{w}.start_year")
            end_ok = self.year(row.get("end_year"), f"{w}.end_year")
            if start_ok and end_ok and row["start_year"] > row["end_year"]:
                self.error(w, "start_year must be <= end_year")

        concepts = self.load_json("concepts.json", "concepts")
        for i, row in enumerate(concepts):
            w = f"concepts.json[{i}]"
            self.add_id("concept", row.get("id"), w)
            for field in ("label", "definition"):
                if not isinstance(row.get(field), str) or not row[field].strip():
                    self.error(w, f"{field} is required and must be a non-empty string")
            if row.get("category") not in CATEGORIES:
                self.error(w, f"category must be one of {sorted(CATEGORIES)}")
            for field in ("aliases", "sources"):
                if field == "aliases":
                    self.strings(row.get(field, []), f"{w}.{field}")
                else:
                    self.urls(row.get(field, []), f"{w}.{field}")

        works = self.load_json("works.json", "works")
        for i, row in enumerate(works):
            w = f"works.json[{i}]"
            self.add_id("work", row.get("id"), w)
            if not isinstance(row.get("title"), str) or not row["title"].strip():
                self.error(w, "title is required and must be a non-empty string")
            for field in ("artist_ids", "place_ids", "concept_ids"):
                values = self.strings(row.get(field, []), f"{w}.{field}")
                target_kind = {"artist_ids": "artist", "place_ids": "place", "concept_ids": "concept"}[field]
                for value in values:
                    if value not in self.ids[target_kind]:
                        self.error(w, f"unknown {target_kind} reference: {value}")
            for field in ("release_year", "recording_year"):
                self.year(row.get(field), f"{w}.{field}", nullable=True)
            self.urls(row.get("source_urls", []), f"{w}.source_urls")

        # JSONL relation endpoints are checked after all entity IDs are loaded.
        relation_file = ATLAS / "relations.jsonl"
        try:
            lines = relation_file.read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            self.error("relations.jsonl", f"cannot read file: {exc}")
            lines = []
        for line_no, line in enumerate(lines, 1):
            if not line.strip():
                continue
            where = f"relations.jsonl:{line_no}"
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                self.error(where, f"invalid JSON: {exc}")
                continue
            if not isinstance(row, dict):
                self.error(where, "each line must be a JSON object")
                continue
            for field in ("source", "target"):
                value = row.get(field)
                if not isinstance(value, str) or ":" not in value:
                    self.error(where, f"{field} must use kind:id syntax")
                    continue
                kind, entity_id = value.split(":", 1)
                if kind not in self.ids:
                    self.error(where, f"unknown entity kind in {field}: {kind}")
                elif entity_id not in self.ids[kind]:
                    self.error(where, f"unknown {kind} reference in {field}: {entity_id}")
            relation = row.get("relation")
            if relation not in RELATIONS:
                self.error(where, f"unknown relation: {relation}")
            if row.get("evidence") not in {"source", "editorial"}:
                self.error(where, 'evidence must be "source" or "editorial"')
            source_urls = row.get("source_urls", [])
            self.urls(source_urls, f"{where}.source_urls")
            if relation == "influenced_by" and (
                row.get("evidence") != "source" or not source_urls
            ):
                self.error(where, "influenced_by requires evidence=source and at least one source URL")

        if self.errors:
            print("Music Atlas validation failed:")
            for item in self.errors:
                print(f"- {item}")
            return 1
        print(
            "Music Atlas validation passed: "
            f"{len(self.ids['artist'])} artists, {len(places)} places, "
            f"{len(eras)} eras, {len(concepts)} concepts, {len(works)} works, "
            f"{sum(1 for x in lines if x.strip())} relations."
        )
        return 0


if __name__ == "__main__":
    sys.exit(Validator().run())

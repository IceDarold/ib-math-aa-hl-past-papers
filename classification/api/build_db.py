#!/usr/bin/env python3
"""Build the read-only SQLite index served by the Question Atlas API."""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path


COLUMNS = (
    "id", "paper", "question", "part", "marks", "calculator", "source_pages",
    "markscheme_pages", "task_summary", "primary_topic", "secondary_topics",
    "method_family", "method_tags", "method_path", "accepted_alternatives",
    "session", "zone", "source_root", "review_status", "evidence", "confidence",
    "review_flags",
)


def text(row: dict[str, object], key: str) -> str:
    return str(row.get(key, ""))


def build(source: Path, output: Path) -> None:
    rows = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(rows, list):
        raise ValueError("The source must be a JSON array of questions")

    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        output.unlink()

    connection = sqlite3.connect(output)
    try:
        connection.execute("PRAGMA journal_mode=OFF")
        connection.execute("PRAGMA synchronous=OFF")
        definitions = ", ".join(f'"{column}" TEXT NOT NULL DEFAULT \'\'' for column in COLUMNS)
        connection.execute(f"CREATE TABLE questions ({definitions}, topic_family TEXT NOT NULL, search_text TEXT NOT NULL, PRIMARY KEY (id))")
        connection.execute("CREATE VIRTUAL TABLE question_fts USING fts5(id UNINDEXED, search_text)")

        insert_columns = ", ".join([f'"{column}"' for column in COLUMNS] + ["topic_family", "search_text"])
        placeholders = ", ".join("?" for _ in range(len(COLUMNS) + 2))
        question_values: list[tuple[str, ...]] = []
        fts_values: list[tuple[str, str]] = []

        for raw in rows:
            if not isinstance(raw, dict) or not text(raw, "id"):
                raise ValueError("Every row needs a non-empty id")
            topic = text(raw, "primary_topic")
            topic_family = topic.split(".", 1)[0]
            searchable = " ".join(text(raw, key) for key in (
                "id", "task_summary", "primary_topic", "secondary_topics", "method_tags",
                "method_family", "method_path", "accepted_alternatives", "session", "zone",
                "review_status", "review_flags",
            ))
            values = tuple(text(raw, column) for column in COLUMNS) + (topic_family, searchable)
            question_values.append(values)
            fts_values.append((text(raw, "id"), searchable))

        connection.executemany(f"INSERT INTO questions ({insert_columns}) VALUES ({placeholders})", question_values)
        connection.executemany("INSERT INTO question_fts (id, search_text) VALUES (?, ?)", fts_values)
        connection.executescript("""
            CREATE INDEX questions_paper_idx ON questions(paper);
            CREATE INDEX questions_calculator_idx ON questions(calculator);
            CREATE INDEX questions_session_idx ON questions(session);
            CREATE INDEX questions_zone_idx ON questions(zone);
            CREATE INDEX questions_status_idx ON questions(review_status);
            CREATE INDEX questions_topic_idx ON questions(topic_family);
            CREATE INDEX questions_method_idx ON questions(method_family);
        """)
        connection.commit()
    finally:
        connection.close()

    print(f"Built {output} from {len(rows)} questions")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    arguments = parser.parse_args()
    build(arguments.source, arguments.output)

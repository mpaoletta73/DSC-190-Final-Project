"""HTML table extraction for sports-reference.com pages.

Sports-reference hides many tables inside HTML comments (<!-- ... -->) to
prevent easy scraping. This module strips those comments and re-parses the
HTML so that all tables are accessible.
"""

import csv
import re
from pathlib import Path

from bs4 import BeautifulSoup, Comment


def _unwrap_commented_tables(html: str) -> str:
    """Replace HTML comments that contain tables with their raw content.

    Sports-reference wraps several stat tables in HTML comments so that
    standard parsers skip them. We find those comments, extract the inner
    HTML, and reinsert it into the document.
    """
    soup = BeautifulSoup(html, "lxml")
    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        if "<table" in comment:
            fragment = BeautifulSoup(str(comment), "lxml")
            comment.replace_with(fragment)
    return str(soup)


def _safe_filename(name: str, fallback: str = "table") -> str:
    """Convert a table id/caption into a safe filename (no extension)."""
    cleaned = re.sub(r"[^\w]+", "_", name).strip("_")
    return cleaned if cleaned else fallback


def extract_tables(html: str) -> list[dict]:
    """Parse *html* and return a list of table dicts.

    Each dict has keys:
        - ``id``: the HTML ``id`` attribute of the table (may be empty)
        - ``caption``: text of the ``<caption>`` element (may be empty)
        - ``headers``: list of column header strings
        - ``rows``: list of row lists (each a list of cell strings)
    Only tables that contain at least one data row are returned.
    """
    unwrapped = _unwrap_commented_tables(html)
    soup = BeautifulSoup(unwrapped, "lxml")

    tables = []
    for table in soup.find_all("table"):
        table_id = table.get("id", "")
        caption_tag = table.find("caption")
        caption = caption_tag.get_text(strip=True) if caption_tag else ""

        # Extract column headers from <thead>
        headers: list[str] = []
        thead = table.find("thead")
        if thead:
            # Use the last header row (some tables have multi-row headers)
            header_rows = thead.find_all("tr")
            if header_rows:
                ths = header_rows[-1].find_all(["th", "td"])
                headers = [th.get_text(strip=True) for th in ths]

        # Extract data rows from <tbody>
        rows: list[list[str]] = []
        tbody = table.find("tbody")
        if tbody:
            for tr in tbody.find_all("tr"):
                # Skip repeated header rows that sports-reference injects
                tr_classes = tr.get("class", [])
                if "thead" in tr_classes or "spacer" in tr_classes:
                    continue
                cells = tr.find_all(["td", "th"])
                if cells:
                    rows.append([c.get_text(strip=True) for c in cells])

        if rows:
            tables.append(
                {
                    "id": table_id,
                    "caption": caption,
                    "headers": headers,
                    "rows": rows,
                }
            )

    return tables


def save_table_as_csv(table: dict, output_dir: str) -> Path:
    """Write *table* to a CSV file inside *output_dir*.

    The filename is derived from the table's ``id``, falling back to its
    ``caption``, and finally to ``"table"``.  A numeric suffix is NOT added
    here; callers are responsible for deduplication if needed.

    Returns the :class:`~pathlib.Path` of the written file.
    """
    name = table["id"] or _safe_filename(table["caption"])
    filepath = Path(output_dir) / f"{name}.csv"

    with filepath.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if table["headers"]:
            writer.writerow(table["headers"])
        writer.writerows(table["rows"])

    return filepath

"""Command-line interface for sports-ref-scraper."""

import os
import sys
from pathlib import Path

import click

from .fetcher import SUPPORTED_DOMAINS, fetch_html, validate_url
from .parser import extract_tables, save_table_as_csv


@click.group()
@click.version_option(package_name="sports-ref-scraper")
def cli() -> None:
    """Sports Reference Scraper.

    Download every stats table from a sports-reference.com page as
    individual CSV files. Handles tables hidden inside HTML comments,
    which are missed by standard parsers.
    """


@cli.command()
@click.argument("url")
@click.option(
    "--output-dir",
    "-o",
    default=".",
    show_default=True,
    help="Directory where CSV files will be saved.",
)
def scrape(url: str, output_dir: str) -> None:
    """Download all tables from URL as CSV files.

    URL must point to a page on one of the supported sports-reference sites
    (run `sportsref sites` to see the full list).

    Each table is saved as a separate CSV file named after the table's HTML
    id attribute (e.g. batting_standard.csv, per_game.csv).

    \b
    Examples:
      sportsref scrape https://www.baseball-reference.com/players/o/ohtansh01.html
      sportsref scrape https://www.basketball-reference.com/players/j/jamesle01.html -o ~/data
      sportsref scrape https://www.pro-football-reference.com/players/M/MahoP00.htm
    """
    try:
        validate_url(url)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc

    click.echo(f"Fetching {url} ...")
    try:
        html = fetch_html(url)
    except Exception as exc:  # noqa: BLE001
        raise click.ClickException(f"Failed to fetch page: {exc}") from exc

    tables = extract_tables(html)
    if not tables:
        click.echo("No tables found on this page.")
        return

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Deduplicate filenames: track names already used this run
    seen: dict[str, int] = {}
    click.echo(f"Found {len(tables)} table(s). Saving to '{output_dir}' ...")

    for table in tables:
        name = table["id"] or table["caption"] or "table"
        count = seen.get(name, 0)
        seen[name] = count + 1
        if count > 0:
            # Append suffix for duplicate names
            base = table["id"] or "table"
            table = dict(table, id=f"{base}_{count}")

        csv_path = save_table_as_csv(table, output_dir)
        label = table["id"] or table["caption"] or "unnamed"
        click.echo(
            f"  {click.style('✓', fg='green')} {csv_path.name}"
            f"  ({len(table['rows'])} rows)"
        )

    click.echo(click.style(f"\nDone. {len(tables)} file(s) saved.", bold=True))


@cli.command()
def sites() -> None:
    """List all supported sports-reference sites."""
    click.echo("Supported sites:")
    for domain in SUPPORTED_DOMAINS:
        click.echo(f"  • https://www.{domain}")

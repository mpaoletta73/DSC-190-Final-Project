# Sports Reference Scraper

A command-line tool that downloads every stats table from any
[sports-reference.com](https://www.sports-reference.com) family page
(Baseball Reference, Basketball Reference, Pro Football Reference, Hockey
Reference) as individual CSV files. It handles the tables that sports-reference
hides inside HTML comments, which are skipped by standard scrapers like
`pandas.read_html`.

## Usage

**Install the tool:**

```bash
uv add "git+https://github.com/mpaoletta73/DSC-190-Final-Project.git"
```

**Scrape all tables from a player or team page:**

```bash
sportsref scrape <url>
```

By default, CSV files are saved to the current directory. Use `-o` to choose a
different folder:

```bash
sportsref scrape <url> -o ~/data/baseball
```

**Examples:**

```bash
# Shohei Ohtani's career stats (Baseball Reference)
sportsref scrape https://www.baseball-reference.com/players/o/ohtansh01.shtml

# LeBron James per-game stats (Basketball Reference)
sportsref scrape https://www.basketball-reference.com/players/j/jamesle01.html -o lebron_data

# Patrick Mahomes career stats (Pro Football Reference)
sportsref scrape https://www.pro-football-reference.com/players/M/MahoP00.htm

# Connor McDavid stats (Hockey Reference)
sportsref scrape https://www.hockey-reference.com/players/m/mcdavco01.html
```

Each table is saved as a separate CSV file named after its HTML id (e.g.
`batting_standard.csv`, `per_game.csv`, `br-salaries.csv`).

**List supported sites:**

```bash
sportsref sites
```

**Get help:**

```bash
sportsref --help
sportsref scrape --help
```


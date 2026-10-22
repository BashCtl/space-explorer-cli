# Space Explorer

Space Explorer is a Python command-line app for NASA data. It retrieves Astronomy Picture of the Day (APOD) entries and near-Earth object (asteroid) data, formats results in the terminal, and can save asteroid plots.

## Requirements

- Python 3.13 or newer
- [uv](https://docs.astral.sh/uv/)
- A NASA API key for near-Earth object requests

## Install

### Editable install with `uv pip`

Create and activate a virtual environment, then install the project in editable mode:

```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

After installation, the `space` command is available directly, and source changes take effect without reinstalling:

```bash
space apod
space asteroids
```

### Install with uv project commands

Alternatively, install the project and development dependencies with:

```bash
uv sync --dev
```

Then run commands through uv:

```bash
uv run space apod
uv run space asteroids
```

## API key

Create a `.env` file in the project root and set your NASA API key:

```dotenv
API_KEY=your_nasa_api_key
```

The client reads `API_KEY` when it starts. APOD requests use the NASA Science website; asteroid requests use the NASA NEO API.

## APOD commands

Show the default result (one recent entry):

```bash
space apod
```

Show a specific day or a date range (`YYYY-MM-DD`):

```bash
space apod --date 2026-10-20
space apod --from 2026-10-01 --to 2026-10-05
```

Request several recent entries or print raw response JSON:

```bash
space apod --recent 5
space apod --raw
```

`--recent` accepts values from 1 to 25. APOD responses are cached for 12 hours.

## Asteroid commands

Show up to ten objects from the default feed, or look ahead by up to seven days:

```bash
space asteroids
space asteroids --days 3
```

You can also provide both ends of an explicit date range:

```bash
space asteroids --start 2026-10-20 --end 2026-10-23
```

The explicit range must be ordered and no longer than seven days. `--days` cannot be combined with `--start` or `--end`. Filter hazardous objects, change the number shown, or save a plot:

```bash
space asteroids --hazardous-only
space asteroids --limit 5
space asteroids --days 3 --plot output/asteroids.png
```

Asteroid responses are cached for 6 hours. `--no-cache` bypasses reading cached data and fetches a fresh response; the response is still saved to the cache. Both commands accept `--timeout SECONDS`, which must be positive.

## Cache

The cache is stored in `.cache/data.json` relative to the current working directory. Different request parameters have separate entries. Expired or malformed entries are treated as cache misses.

## Development

Install the development dependencies and run tests with:

```bash
uv sync --dev
uv run pytest
```

The tests use saved response fixtures under `tests/data` and mock API calls, so live NASA requests are not needed for the unit suite.

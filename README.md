## YLERobo

A backend for automatically downloading series from YLE Areena. Currently uses yle-dl for performing the downloads.


## Usage

```sh
# Initialize database
ylerobo init

# Add series to be tracked.
# Specify --weekly/--daily/--once to select when to download.
ylerobo add AREENA-URL

# List series in database
ylerobo list

# Performn download of new episodes.
ylerobo download

# Run web service.
ylerobo serve
```

## Environment variables

- `YLEROBO_DB`: Path to the sqlite database. Default: `ylerobo.db`.
- `YLEDL_PARAMS`: Parameters given to yle-dl. Default: `--destdir storage`.


## Planned items

- docker image
- use YLE Areena account information to select series
- migration when database schema changes


## Dev notes

Run tests:
```sh
poetry run pytest -rP
```

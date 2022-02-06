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


## Planned items

- docker image
- use YLE Areena account information to select series
- allow custom parameters for yle-dl (e.g. directories, naming, etc)
- configuration file / environment variables
- database version, migration support


## Dev notes

Run tests:
```sh
poetry run pytest -rP
```

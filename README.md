# Data Contract Guardian

A local data-quality workbench with immutable schema versions, CSV/JSON validation, breaking-change comparison, and a CLI suitable for CI pipelines. Built with Python, FastAPI, SQLite, and a browser interface.

## Run

Requires Python 3.11+.

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
uvicorn guardian.api:app --host 127.0.0.1 --port 8001
```

Open http://127.0.0.1:8001. Save the prefilled sample contract, then validate the sample dataset to see duplicate IDs, invalid enum values, and a negative spend. You can import files, paste data, download reports, and compare saved contract versions. `/docs` contains the API documentation.

## Contract format

See `examples/customers.contract.json`. Each field has a `type`: string, integer, number, or boolean. Options are `required` (default true), `nullable` (default false), `unique`, `enum`, and numeric `min`/`max`. Extra fields are rejected unless `allow_extra` is true. Null values do not participate in uniqueness checks. JSON types are strict: booleans are not integers. CSV values are explicitly converted using field types; empty cells are treated as null. An empty dataset passes vacuously; add a pipeline row-count check if your use case requires records.

The comparison flags constraints that reject previously allowed records, including required additions, type changes, narrower ranges, and enum restrictions. It is a conservative structural comparison, not a proof about downstream consumer compatibility.

## CLI / CI

The core CLI uses only the Python standard library:

```sh
python -m guardian.cli validate examples/customers.contract.json examples/customers.json
python -m guardian.cli validate contract.json incoming.csv --format csv
python -m guardian.cli compare previous.contract.json next.contract.json
```

Exit codes: 0 passed, 1 validation failure or breaking change, 2 malformed input. The included sample intentionally exits 1.

## Tests

```sh
python -m unittest discover -s tests -v
```

Initial verification: 10 tests passed, including real FastAPI requests through TestClient. The UI JavaScript passed a syntax check; interactive browser testing was unavailable in the managed environment.

## Storage and limits

Contract history is persisted in `data/guardian.sqlite` (override with `GUARDIAN_DB`). Versions are assigned inside a database transaction. Reports and uploaded datasets are not stored on the server. Requests are limited to 2 MB, datasets to 10,000 rows, and reports to the first 500 issues while retaining total counts.

This is a single-user local MVP without authentication. Keep it on loopback. PostgreSQL, a React frontend, access control, and a scheduled ingestion worker are future extensions; this version uses SQLite and plain browser JavaScript to keep setup small.

MIT licensed.

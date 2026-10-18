# Weather Pipeline (Docker + PostgreSQL)

The same weather pipeline, moved into Docker. Docker Compose starts a PostgreSQL database and a Python container that loads current weather data from the Open-Meteo API into it.

## How it works

Open-Meteo API → Python container → PostgreSQL container

- `pipeline.py` fetches the data, cleans it, and inserts it into a `weather` table.
- Rerunning doesn't create duplicates (`ON CONFLICT DO NOTHING`).
- Database settings are read from environment variables, and the script retries the connection while Postgres starts.
- Data is kept in a Docker volume, so it survives restarts.

## Run it

Requires Docker Desktop.

```
docker compose up --build -d
docker compose logs pipeline
docker compose exec db psql -U weather -d weather -P pager=off -c "SELECT * FROM weather;"
```

Run it again for new data:

```
docker compose run --rm pipeline
```

Stop it (data is kept):

```
docker compose down
```

## Limitations

The demo database password is written in `docker-compose.yml`. A real project would keep it in a `.env` file that isn't committed (the earthquake pipeline does this).

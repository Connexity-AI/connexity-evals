# connexity

## Quick start (Docker)

Prebuilt images live on [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry). Use a **public** package (or inherit visibility from a public repo) so pulls work without logging in.

```bash
git clone https://github.com/Connexity-AI/connexity.git
cd connexity

cp .env.example .env
# Edit .env: set SITE_URL, JWT_SECRET_KEY, ENCRYPTION_KEY, POSTGRES_PASSWORD, optional API keys.

docker compose up
```

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **API docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **DB UI (pgweb)**: [http://localhost:8083](http://localhost:8083)

The compose file sets **`API_URL=http://backend:8000`** inside the frontend container so the Next.js server talks to FastAPI over the Docker network. You usually only set **`SITE_URL`** to the URL people open in the browser (`http://localhost:3000` locally, or `https://…` when hosted).

**Forks / custom images**: override in `.env`:

```env
CONNEXITY_BACKEND_IMAGE=ghcr.io/your-org/connexity-backend:latest
CONNEXITY_FRONTEND_IMAGE=ghcr.io/your-org/connexity-frontend:latest
```

**Build images locally** (contributors):

```bash
docker compose -f docker-compose.yml -f docker-compose.build.yml up --build
# or: make docker-build-up
```

## Local development (DB in Docker, apps on host)

Prerequisites: [Docker Desktop](https://www.docker.com/products/docker-desktop/), [uv](https://docs.astral.sh/uv/), [Node.js](https://nodejs.org/) + [pnpm](https://pnpm.io/), [GNU Make](https://www.gnu.org/software/make/).

One env file at the repo root (same `.env` as Docker). It includes **`API_URL=http://localhost:8000`** and **`POSTGRES_SERVER=localhost`** so the backend and Next.js dev server reach Postgres on the host port.

```bash
cp .env.example .env
make install
make db
make db-upgrade
make dev          # terminal 1 — backend
make dashboard    # terminal 2 — frontend (loads root .env)
```

## CLI against a hosted instance

Point the CLI at the **public API base URL** (same host as the app if you reverse-proxy `/api/v1`, or a dedicated API host). See [`.env.example`](.env.example) (`CONNEXITY_CLI_API_URL` / `CONNEXITY_CLI_API_TOKEN`).

## Accounts

The database starts empty. Sign up in the UI or via `POST /api/v1/users/signup`.

## Further docs

- [docs/running.md](docs/running.md) — detailed local setup
- `make help` — Make targets

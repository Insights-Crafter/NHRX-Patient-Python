# NHRX deployment guide: Docker Compose on AWS EC2

This guide packages the existing plain HTML/CSS/JavaScript portal and FastAPI backend as separate Docker services. Nginx serves the frontend and proxies `/api/...` to FastAPI over a private Compose network. PostgreSQL is installed directly on the EC2 host, outside Docker Compose; `host.docker.internal` maps to the host gateway so the backend container can reach it. Compose does not create or publish a database service.

## What was inspected

- Frontend: static files in `frontend/`; entry page `index.html` redirects to `login.html`.
- Backend: `app.main:app`, served by Uvicorn. Existing routes are `/auth/login`, `/patients/register`, `/patients/me`, `/patients/me/address`, `/patients/me/updateAdress`, and `/patients/me/updateContact`.
- Database: PostgreSQL on the EC2 host through `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, and `DB_NAME` in `app/database/database.py`. The Compose backend uses `DB_HOST=host.docker.internal`.
- Secrets: `JWT_SECRET_KEY` signs access tokens. `AES_SIV_KEY` encrypts patient data and must remain compatible with already encrypted values.
- Auth: the frontend stores the access token in local storage and sends `Authorization: Bearer ...` on authenticated calls.
- Migrations: no Alembic configuration or migration directory was found. The old startup hook called SQLAlchemy `create_all`; it is now disabled by default. It can be explicitly enabled for local development with `CREATE_DB_TABLES=true`. Production schema changes should use reviewed migrations, preferably Alembic, after a backup; do not enable table creation as a production migration plan.
- The repository contains a local `.env`; it is ignored by Git and Docker build context. It was not copied into an image or displayed. `.env.example` contains placeholders only.

## Local Docker smoke test

Prerequisites: Docker Engine and the Compose plugin (Docker Desktop on Windows/macOS also works), plus PostgreSQL installed on the Docker host and configured to accept connections from the Compose network. Copy `.env.example` to `.env` only if you do not already have a real local `.env`; set the database and key values before starting. Never replace the AES key if the database contains data encrypted with an existing key.

```sh
docker compose config
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 backend
docker compose logs --tail=100 frontend
```

Open `http://localhost/`. The API is reached through the same origin: `http://localhost/api/` is proxied to FastAPI's `/` health endpoint; for example, `http://localhost/api/auth/login` maps to `/auth/login` in FastAPI. The backend container has no published host port. Stop the stack with `docker compose down` (this does not delete or modify the external database).

## Initial EC2 deployment

### 1. Launch the instance

Use a current Ubuntu Server LTS EC2 AMI on a supported 64-bit architecture. Select an instance size appropriate to the project and expected traffic; the smallest instance may run out of memory during Python image builds. Attach an adequate encrypted EBS volume and choose a VPC/subnet with internet access for package and image downloads.

An automatically assigned public IPv4 address can change after stop/start. Allocate and associate an Elastic IP if a stable address is needed; AWS may charge for public IPv4 use. Record the resulting public IPv4 as `EC2_PUBLIC_IPV4`; the public site URL will be `http://EC2_PUBLIC_IPV4/` initially.

Official references: [Launch an EC2 instance](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/LaunchingAndUsingInstances.html), [Elastic IP addresses](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/elastic-ip-addresses-eip.html).

### 2. Configure network access

In the EC2 security group, allow inbound:

| Protocol/port | Source | Purpose |
| --- | --- | --- |
| TCP 22 | Your current public IP `/32` only | SSH administration |
| TCP 80 | `0.0.0.0/0` (and `::/0` only if IPv6 is configured) | Initial HTTP demo |
| TCP 443 | `0.0.0.0/0` (and `::/0` only if IPv6 is configured) | HTTPS after TLS is configured |

Do **not** add port 8000. Docker publishes only Nginx port 80; Uvicorn is reachable only on the internal Compose network. Restrict SSH to your own address and update it when that address changes. Ensure the VPC network ACL and Ubuntu firewall also permit the selected web ports. If using UFW, allow SSH before enabling it, then allow 80 and 443.

For this setup, PostgreSQL runs on EC2 itself. Do not add TCP 5432 to the EC2 security group. PostgreSQL must listen on the host's Docker gateway interface (or another host interface reachable from the bridge), and `pg_hba.conf` should allow only the Compose network CIDR for the intended database/user. Keep host firewall rules restrictive. If PostgreSQL later moves to RDS, allow TCP 5432 from the EC2 security group only over private networking; never expose it to the whole internet.

Official references: [EC2 security group rules](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-rules.html), [Security group best practices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/security-group-rules-reference.html).

### 3. Install Docker Engine and Compose on Ubuntu

Follow Docker's official [Ubuntu installation instructions](https://docs.docker.com/engine/install/ubuntu/), including its apt repository setup, and install `docker-ce`, `docker-ce-cli`, `containerd.io`, `docker-buildx-plugin`, and `docker-compose-plugin`. Verify:

```sh
sudo docker run hello-world
docker compose version
```

You can prefix Docker commands with `sudo`. Adding your login user to the `docker` group avoids `sudo`, but that group grants root-equivalent host access; log out and back in after adding it and treat membership accordingly.

### 4. Clone the project and create server secrets

```sh
sudo apt-get update
sudo apt-get install -y git
git clone <YOUR_GITHUB_REPOSITORY_URL> nhrx
cd nhrx
cp .env.example .env
nano .env
chmod 600 .env
```

Fill in the PostgreSQL credentials and keys. `.env.example` sets `DB_HOST=host.docker.internal`; Compose maps that name to the EC2 Docker host gateway. Set `CREATE_DB_TABLES=false`. Supply `JWT_SECRET_KEY` securely. If existing encrypted patient data is used, retrieve and preserve the **exact existing** `AES_SIV_KEY`; a new key cannot decrypt old values. Do not put `.env` in Git, paste its contents into logs, or bake it into either image. For a team project, restrict repository and EC2 access and plan a proper secret manager before real production data.

PostgreSQL commonly listens only on `127.0.0.1` initially, which a bridge container cannot reach. Start the Compose stack, then inspect its network and PostgreSQL configuration paths:

```sh
docker compose up -d --build
docker network ls
docker network inspect <COMPOSE_NETWORK_NAME>
docker compose exec backend python -c "import socket; print(socket.gethostbyname('host.docker.internal'))"
sudo -u postgres psql -c "SHOW config_file;"
sudo -u postgres psql -c "SHOW hba_file;"
```

Read the network `Subnet` from `docker network inspect`. The Python command prints the exact host gateway address assigned to `host.docker.internal`. Configure PostgreSQL to listen on that address (avoid binding public interfaces when possible). Add a narrow `pg_hba.conf` rule using the actual database name, user, and Compose network CIDR:

```conf
host    <DB_NAME>    <DB_USER>    <COMPOSE_SUBNET_CIDR>    scram-sha-256
```

Restart PostgreSQL using the service/cluster name installed on the instance, then check its listener with `sudo ss -lntp 'sport = :5432'`. Keep AWS inbound TCP 5432 closed and do not add a public UFW allow rule. If the Compose network is recreated with a different subnet, update the corresponding `pg_hba.conf` rule. Verify DB connectivity with a database-backed application request; the API health endpoint only confirms that FastAPI is running.

### 5. Validate, start, and verify

```sh
docker compose config
docker compose up -d --build
docker compose ps
docker compose logs --tail=100 backend
docker compose logs --tail=100 frontend
curl -i http://127.0.0.1/
curl -i http://127.0.0.1/api/
```

Then open `http://EC2_PUBLIC_IPV4/` from a browser. A 200 response from `/api/` verifies the proxy and API process; it does not prove database credentials work. Test database-backed registration/login only with approved non-production test data and a non-production database. The backend API can also be checked from the Compose network with:

```sh
docker compose exec frontend wget -qO- http://backend:8000/
```

No AWS resources are created by this repository setup. A public IP alone does not make the application reachable: Uvicorn/Nginx must listen inside their containers, Compose must publish port 80, the EC2 security group and instance firewall must allow it, and the instance must have a working public route.

## HTTPS and handling health information

The included Nginx configuration provides HTTP only, suitable for initial connectivity checks with synthetic data. Login credentials, JWTs, and patient data must **not** be sent over plain HTTP. Before using real patient information, configure TLS on port 443 (for example, a domain name plus a certificate automation/reverse proxy), redirect HTTP to HTTPS, establish appropriate access controls, backups, monitoring, and secret management, and review applicable privacy/security obligations. Do not treat this student deployment as production-ready for real patient records.

## Future updates

1. Develop and test changes locally; review schema changes separately.
2. Commit and push the intended branch to GitHub.
3. SSH into EC2 and enter the checkout: `cd ~/nhrx`.
4. Pull the deployment branch: `git pull origin main` (replace `main` if needed).
5. For a backend-only code/dependency change: `docker compose up -d --build --force-recreate backend frontend`. Recreate frontend too so Nginx reconnects cleanly to a recreated backend container. For frontend HTML/CSS/JS or Nginx config changes, rebuild `frontend`; if frontend JavaScript changes its `/api` path or proxy contract, coordinate both sides.
6. For Compose, Dockerfile, shared build-context, or dependency changes, validate and rebuild both: `docker compose config` then `docker compose up -d --build`.
7. Check `docker compose ps`, logs, `/`, and `/api/` before considering the update complete.

For schema changes, first take and verify a PostgreSQL backup, store encrypted backups off the instance, and practice restoring them. Review an Alembic migration (none is currently configured), apply it deliberately against the intended database, then deploy compatible code. Do not run `Base.metadata.drop_all`, reset the database, or assume a Git rollback reverses a migration. An EBS snapshot alone is not necessarily a database-consistent backup unless PostgreSQL is quiesced or the snapshot process is coordinated. Rollback guidance: redeploy the last known-good application commit/image; restore a database backup only through an approved recovery plan. Some migrations require a forward fix or coordinated code/data rollback, and Git alone cannot restore prior database data.

## Troubleshooting

Run these commands from the repository checkout:

```sh
docker compose ps
docker compose logs --tail=200 backend
docker compose logs --tail=200 frontend
docker compose exec frontend nginx -t
docker compose exec frontend wget -S -O- http://backend:8000/
```

- **Container exits / import error:** inspect backend logs; confirm Compose builds from repository root and the command remains `app.main:app`. Check all required packages are pinned in `requirements.txt` and rebuild backend.
- **Missing environment variable:** check names (not values) against `.env.example`; ensure `.env` exists on EC2, has mode `600`, and `docker compose config` succeeds. Never share its values in an issue/log.
- **Database connection fails:** verify `DB_HOST=host.docker.internal`, Compose `extra_hosts`, PostgreSQL `listen_addresses`, the Compose subnet rule in `pg_hba.conf`, DB name/user/password, and host firewall. Check backend logs. Do not publish or allow TCP 5432 from the public internet.
- **HTTP 404:** verify exact route spelling and methods above; the existing update route uses the spelling `/patients/me/updateAdress`. Browser URLs prepend `/api`, while FastAPI routes do not.
- **HTTP 502:** Nginx cannot reach FastAPI. Check backend health/logs and `docker compose exec frontend wget -S -O- http://backend:8000/`; check the Compose network and Nginx proxy target.
- **HTTP 504:** inspect backend/database response latency, pool/connectivity, and Nginx timeout logs. Increase a timeout only after identifying the slow operation.
- **Nginx syntax/startup error:** run `docker compose exec frontend nginx -t`, then inspect frontend logs. Check `frontend/nginx.conf` syntax and rebuild frontend after edits.
- **JWT/auth failure:** verify the login response, browser request's `Authorization: Bearer ...` header, system clock, and that `JWT_SECRET_KEY` is stable between deployments. Changing it invalidates existing tokens.
- **Encryption/decryption failure:** confirm `AES_SIV_KEY` matches the key that encrypted existing database values. Do not rotate it without a data migration plan.
- **File upload / request too large:** there are no upload endpoints in the inspected routes. If one is added, review validation/storage and raise `client_max_body_size` in `frontend/nginx.conf` only to a justified limit, then rebuild frontend.
- **Frontend asset missing:** check browser network requests and ensure paths are relative to the static site; inspect Nginx logs and rebuild frontend.
- **Public site times out:** confirm `docker compose ps` shows frontend healthy, `docker compose port frontend 80` maps host port 80, security group permits 80, instance firewall permits 80, and a public subnet/route exists. Port 8000 should remain closed publicly. SSH should be limited to your own IP.

No GitHub Actions or unattended production deployment is configured. CI/CD can be added later after secrets, approval gates, image tagging, and rollback practices are agreed on.

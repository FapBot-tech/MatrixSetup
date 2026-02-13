# Matrix Synapse Docker Setup

A ready-to-use [Matrix Synapse](https://matrix.org/docs/projects/server/synapse/) server stack with Nginx reverse proxy, PostgreSQL, and custom moderation modules. This project is designed for easy local or small-scale deployment.

---

## Features
- **Matrix Synapse** server with custom configuration
- **Nginx** reverse proxy with SSL support
- **PostgreSQL** database
- **Custom moderation modules** (see `modules/`)
- **Static web frontend** (see `public_html/`)
- **Admin panel** available at `admin.$DOMAIN`


Matrix will end up running on `msg.$DOMAIN`, the static web client on `chat.$DOMAIN`, and the admin panel on `admin.$DOMAIN`.

---

## Prerequisites
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/) installed
- A domain name (for production use)

---

## Quick Start

### 1. Create a `.env` file
Create a `.env` file in the project root with the following content:
```dotenv
POSTGRES_PASSWORD=your_POSTGRES_PASSWORD
DOMAIN=your.domain
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443
```
Replace `your_POSTGRES_PASSWORD` and `your.domain` with your own values.

### 2. Add SSL certificates
Add an SSL certificate that covers all subdomains `msg.$DOMAIN`, `admin.$DOMAIN` and `chat.$DOMAIN` to the `nginx-certs/` folder:
- Place your full certificate chain as `nginx-certs/fullchain.pem`
- Place your private key as `nginx-certs/privkey.pem`

You can use [Let's Encrypt](https://letsencrypt.org/) or another certificate authority. Make sure the certificate is valid for both subdomains.

### 3. Start the containers
```sh
docker compose up
```

### 4. Register your first user
```sh
docker exec -it synapse-2 register_new_matrix_user http://localhost:8008 -c /data/homeserver.yaml
```
Follow the prompts to set a username and password.

### 5. Configure your server
Edit `homeserver.yaml` in the `data/` directory to customize your server settings. See [Synapse documentation](https://element-hq.github.io/synapse/latest/usage/configuration/config_documentation.html) for all options.

After making changes, rebuild and restart:
```sh
docker compose build --no-cache && docker compose up
```

---

## Custom Modules
Custom moderation and utility modules are located in the [`modules/`](modules/) directory:
- `channel_config_command.py`
- `edit_blocker.py`
- `file_type_filter.py`
- `private_message_file_blocker.py`
- `room_restrict.py`
- `word_filter.py`

These are automatically copied into the Synapse container and enabled via configuration.

---

## Static Web Frontend
The `public_html/` directory contains a static web client, served at `https://chat.<your.domain>` via Nginx.

---

## Troubleshooting
- **Logs:** Check `data/homeserver.log` for Synapse logs.
- **Configuration:** Ensure your `.env` and `homeserver.yaml` are correct.
- **Ports:** Make sure ports 80/443 (or those set in `.env`) are open and not in use.
- **Certificates:** Place your SSL certs in `nginx-certs/` as `fullchain.pem` and `privkey.pem`.

---

## Useful Links
- [Matrix Synapse Documentation](https://element-hq.github.io/synapse/latest/)
- [Matrix Spec](https://spec.matrix.org/)

---

## License
See [LICENSE](LICENSE) if present, or assume AGPL-3.0 as per Synapse upstream.

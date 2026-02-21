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
(these domains can be configured in `nginx.conf.template`, though keep in mind that changing the Matrix domain also requires chanegs to the `homeserver.yaml`. Once the Matrix server has been setup, it's domain should not be changed. Of course you're also more than welcome to not use the nginx webserver and setup your own proxies, again check `nginx.conf.template` to see which port should go where.)

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
(If you don't want to use the nginx, remove the sefvice from the dockerfile and skip this step)

Add an SSL certificate that covers all subdomains `msg.$DOMAIN`, `admin.$DOMAIN` and `chat.$DOMAIN` to the `nginx-certs/` folder:
- Place your full certificate chain as `nginx-certs/fullchain.pem`
- Place your private key as `nginx-certs/privkey.pem`

You can use [Let's Encrypt](https://letsencrypt.org/) or another certificate authority. Make sure the certificate is valid for both subdomains.

### 3. Start the containers
```sh
docker compose up
```

### 4. Configure your server
Edit `homeserver.yaml` in the `data/` directory to customize your server settings. See [Synapse documentation](https://element-hq.github.io/synapse/latest/usage/configuration/config_documentation.html) for all options.

After making changes, rebuild and restart:
```sh
docker compose build --no-cache && docker compose up
```

Then finally we'll need to update the Cinny config to show the correct domain for login. Header over to `./public_html/config.json` and replace
the `homeserverList` value with the correct domain, eg:
```json

{
  "defaultHomeserver": 0,
  "homeserverList": [
    "msg.example.com"
  ],
  "allowCustomHomeservers": false,
  "featuredCommunities": {
    "openAsDefault": false,
    "spaces": [],
    "rooms": [
      "#general:msg.example.com"
    ],
    "servers": []
  },
  "hashRouter": {
    "enabled": true,
    "basename": "/"
  }
}

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

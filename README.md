# Matrix Synapse Deployment (v1.114.0)

This repository contains a production-ready Matrix Synapse deployment using **PostgreSQL 16** and custom **Python spam-filtering modules**.

## 🚀 Getting Started

### 1. Prerequisites
* Docker and Docker Compose installed.
* A domain name (e.g., `chat.your.domain`) pointing to your host IP.
* An existing Docker volume named `synapse-data` (or change `external: true` to `false` in `docker-compose.yaml`).

Before running the stack, create a `.env` file in the root directory:

```bash
echo "POSTGRES_PASSWORD=your_secure_password" > .env

docker run -it --rm \
    --mount type=volume,src=synapse-data,dst=/data \
    -e SYNAPSE_SERVER_NAME=my.matrix.host \
    -e SYNAPSE_REPORT_STATS=yes \
    matrixdotorg/synapse:latest generate
```

Then make sure the password in your homeserver.yaml matches whatever you've got in your env

### 2. Installation & Build
Build the custom image (which includes the `python-magic` dependencies and custom modules) and start the stack:

```bash
docker compose up -d

```

* **URL:** `http://localhost:8008`

### 3. Create an Admin User

Run the following command to create your first user. You will be prompted for a password and asked if the user should be an admin (choose **yes**):

```bash
docker exec -it synapse register_new_matrix_user http://localhost:8008 -c /data/homeserver.yaml

```

---

## 🛠 Administration & UI

### Synapse Admin Interface

To manage users, rooms, and server settings via a GUI, run the Synapse Admin tool:

```bash
docker run -d -p 8080:80 --name synapse-admin awesometechnologies/synapse-admin

```

* **URL:** `http://localhost:8080`

### Matrix Web Client (Cinny)

1. Download the latest release from the [Cinny GitHub Releases](https://www.google.com/search?q=https://github.com/cinnyapp/cinny/releases).
2. Upload the static files to the root directory of your web host (Nginx/Apache).
3. Login using your homeserver URL.

---

### Power Level Defaults

This server is configured with a **"Read-Only by Default"** policy for new rooms:

* **Messaging Level:** 10 (Required to send messages).
* **New User Level:** 10 (Users join with this level).
* **Muting:** To mute a user, an admin simply demotes that user's Power Level to **0** via the room settings.

---

## 🌐 Reverse Proxy Configuration (Apache)

To allow users to connect via a standard domain without specifying port `8008`, use the following Apache proxy configuration:

```apache2
<VirtualHost *:80>
    ServerName msg.fapbot.tech

    ProxyRequests On
    ProxyPass / http://localhost:8008/
    ProxyPassReverse / http://localhost:8008/
    
    # Optional: Preserve Host for Synapse logging
    ProxyPreserveHost On
</VirtualHost>

```

## ⚙️ Configuration Files
* **homeserver.yaml:** Main Synapse configuration file located in the `synapse-data` volume.
* **docker-compose.yaml:** Docker Compose file defining services, volumes, and networks.
* **Dockerfile:** Custom Dockerfile for building the Synapse image with additional modules.

## 📝 Maintenance Note

* **Image Lock:** The `Dockerfile` is pinned to a specific SHA digest (`v1.114.0@sha256:3c0725...`) to ensure long-term stability across different environments.
* **Database:** Uses **PostgreSQL 16-alpine**. Database credentials match between `docker-compose.yaml` and `homeserver.yaml`.
* **Python Version:** Custom modules are installed into the `python3.13` site-packages directory to match the base image environment.


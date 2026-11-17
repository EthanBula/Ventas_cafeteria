FROM python:3.11-slim as builder
WORKDIR /app
RUN apt-get update && apt-get install -y unzip curl
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN reflex init
RUN reflex export --frontend-only --no-zip

FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y debian-keyring debian-archive-keyring apt-transport-https curl && \
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg && \
        curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list && \
            apt-get update && apt-get install caddy
            COPY requirements.txt .
            RUN pip install -r requirements.txt
            COPY . .
            COPY --from=builder /app/.web/build/client /app/public
            COPY Caddyfile /etc/caddy/Caddyfile
            CMD caddy start --config /etc/caddy/Caddyfile && reflex run --env prod --backend-only
            

# Build stage
FROM ubuntu:20.04 as build

RUN apt update && apt install -y curl unzip xz-utils git

# Optional: install Flutter to build here (only if not pre-built)
# You can skip this block if you're committing `build/web` directly

# Serve prebuilt Flutter web app
FROM nginx:alpine

COPY ./build/web /usr/share/nginx/html
COPY ./default.conf /etc/nginx/conf.d/default.conf
RUN chmod -R 755 /usr/share/nginx/html
# Optional: configure Nginx for SPA routing
#COPY nginx.conf /etc/nginx/conf.d/default.conf
# Multi-stage build for TMNA Disruption Manager RIM Frontend
FROM node:22-slim as build

WORKDIR /app

# Copy shared config first (from context root)
COPY shared_config.json ./

WORKDIR /app/frontend

# Copy dependency manifests and install
COPY frontend/package*.json ./
RUN npm ci

# Copy application source
COPY frontend/ ./

# Build application
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Set backend host as build arg with default
ARG BACKEND_HOST=backend
ENV BACKEND_HOST=${BACKEND_HOST}

# Copy built assets
COPY --from=build /app/frontend/dist /usr/share/nginx/html

# Copy nginx configuration template
COPY frontend/nginx.conf.template /etc/nginx/templates/default.conf.template

# Expose frontend port
EXPOSE 80

# nginx will automatically process templates in /etc/nginx/templates/
CMD ["nginx", "-g", "daemon off;"]

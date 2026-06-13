# frontend/Dockerfile — el build context es la RAÍZ del repo (ver docker-compose.yml).
#
# Etapa 1: compilar el bundle de React con Vite.
FROM node:20-alpine AS build
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ .
RUN npm run build

# Etapa 2: servir los estáticos y hacer de proxy /api -> backend con nginx.
FROM nginx:alpine
COPY frontend/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80

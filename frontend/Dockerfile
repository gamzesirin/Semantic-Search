# Frontend (React) için 2 aşamalı Docker imajı.
# 1) Node ile statik build üret  2) nginx ile servis et.

# --- Aşama 1: build ---
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
# .env.production (REACT_APP_API_BASE) build sırasında otomatik gömülür
RUN npm run build

# --- Aşama 2: servis ---
FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

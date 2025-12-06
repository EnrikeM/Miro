# Stage 1: build the Vite application
# Use a glibc-based image to avoid missing optional native rollup dependencies on musl.
FROM node:20-slim AS build
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Copy source code and configuration
COPY tsconfig*.json vite.config.ts eslint.config.js index.html .
COPY src ./src

# Build the production bundle with API URL baked in
ARG VITE_API_URL=http://localhost:8080
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build

# Stage 2: serve static assets with nginx
FROM nginx:stable-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

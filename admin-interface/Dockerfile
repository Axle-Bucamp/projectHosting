# --- Stage 1: Build ---
FROM node:20-alpine AS builder

# Enable and prepare pnpm
RUN corepack enable && corepack prepare pnpm@10.4.1 --activate

WORKDIR /app

# Add build-time argument for API URL
ARG VITE_API_URL=http://localhost:8000

# Make it available at build time
ENV VITE_API_URL=$REACT_APP_API_URL

# Copy dependency manifests first (leverage cache)
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy rest of the app
COPY . .

# Build the app with the API URL baked in
RUN pnpm build

# --- Stage 2: Serve with Nginx ---
FROM nginx:alpine AS runner

# Copy the built output from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Optional: Uncomment to support SPA routing with Nginx
# COPY ./nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

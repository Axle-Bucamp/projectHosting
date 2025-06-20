# --- Stage 1: Build ---
FROM node:20-alpine AS builder

# Install pnpm globally
RUN corepack enable && corepack prepare pnpm@10.4.1 --activate

WORKDIR /app

# Copy only necessary files first to leverage Docker cache
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy the full source
COPY . .

# Build the app
RUN pnpm build

# --- Stage 2: Serve ---
FROM nginx:alpine AS runner

# Copy built files to nginx default directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Optional: replace default nginx.conf for SPA routing
#COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

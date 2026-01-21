# Stage 1: Build Node app
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY package.json package-lock.json* ./
RUN npm install

# Copy the rest of the source code and build
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:stable-alpine

# Copy built files from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Use template Nginx config that listens on $PORT
COPY default.conf.template /etc/nginx/conf.d/default.conf.template

# Expose port 8080 (Cloud Run maps $PORT internally)
EXPOSE 8080

# Replace $PORT in nginx config at runtime and start Nginx
CMD sh -c "envsubst '\$PORT' < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"

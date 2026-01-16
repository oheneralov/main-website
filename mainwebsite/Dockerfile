# Build stage: install dependencies and create the production bundle
FROM node:20-alpine AS build
WORKDIR /app

# Install dependencies first to leverage layer caching
COPY package*.json ./
RUN npm install

# Copy the rest of the project and build
COPY . .
RUN npm run build

# Runtime stage: serve the static assets with nginx
FROM nginx:1.27-alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

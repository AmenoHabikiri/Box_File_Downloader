# Use official Node.js LTS image
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build TypeScript
RUN npm install -g typescript && \
    npm run build && \
    npm uninstall -g typescript

# Create downloads directory
RUN mkdir -p /app/downloads

# Set environment to production
ENV NODE_ENV=production

# Run the application
CMD ["node", "dist/index.js"]

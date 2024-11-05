# Frontend Dockerfile

# Use an official Node.js image
FROM node:16 AS development

# Set the working directory
WORKDIR /frontend

# Copy package.json and package-lock.json for dependency installation
COPY frontend/graphdb/package*.json ./

# Install frontend dependencies
RUN npm install

# Copy the rest of the frontend source code
COPY frontend/graphdb/ .

# Run the React development server to enable hot-reloading
CMD ["npm", "start"]

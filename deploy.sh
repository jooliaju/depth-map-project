#!/bin/bash

# Build frontend
cd frontend
npm run build

# Copy frontend build to backend static folder
cp -r build/* ../backend/static/

# Set production environment variables
export FLASK_ENV=production
export FRONTEND_URL=https://yourdomain.com
export BACKEND_URL=https://api.yourdomain.com

# Start backend server
cd ../backend
python -m waitress-serve --call 'api.app:create_app' 
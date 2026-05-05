#!/usr/bin/env bash
set -o errexit

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Building React frontend..."
cd frontend
npm install --omit=dev
NODE_ENV=production npm run build
cd ..

echo "Copying frontend build to static files..."
mkdir -p myproject/static
cp -r frontend/build/* myproject/static/ || true

echo "Collecting Django static files..."
python myproject/manage.py collectstatic --no-input

echo "Running database migrations..."
python myproject/manage.py migrate

echo "Build completed successfully!"

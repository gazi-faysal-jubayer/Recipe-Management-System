#!/bin/bash

# Frontend Deployment Script for Vercel

set -e

echo "🚀 Starting frontend deployment..."

# Navigate to frontend directory
cd "$(dirname "$0")/../frontend"

echo "📦 Installing dependencies..."
npm ci

echo "🏗️  Building application..."
npm run build

echo "✅ Frontend build complete!"
echo "Use 'vercel --prod' to deploy"

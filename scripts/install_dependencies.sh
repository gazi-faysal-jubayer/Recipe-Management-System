#!/bin/bash

# Installation script for all dependencies

echo "🚀 Recipe Management System - Dependency Installation"
echo "======================================================"

# Check Python
echo "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi
python_version=$(python3 --version)
echo "✓ Found: $python_version"

# Check Node.js
echo "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 20+"
    exit 1
fi
node_version=$(node --version)
echo "✓ Found: Node.js $node_version"

# Install Backend Dependencies
echo ""
echo "📦 Installing Backend Dependencies..."
cd backend
python3 -m venv venv

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

pip install --upgrade pip
pip install -r requirements/development.txt
echo "✓ Backend dependencies installed"

# Install Frontend Dependencies
echo ""
echo "📦 Installing Frontend Dependencies..."
cd ../frontend
npm install
echo "✓ Frontend dependencies installed"

# Check for Tesseract
echo ""
echo "Checking Tesseract OCR..."
if command -v tesseract &> /dev/null; then
    tesseract_version=$(tesseract --version | head -n 1)
    echo "✓ Found: $tesseract_version"
else
    echo "⚠️  Tesseract OCR not found. Image parsing will not work."
    echo "Install instructions:"
    echo "  Windows: https://github.com/UB-Mannheim/tesseract/wiki"
    echo "  macOS: brew install tesseract"
    echo "  Linux: sudo apt install tesseract-ocr"
fi

# Check for Redis
echo ""
echo "Checking Redis..."
if command -v redis-cli &> /dev/null; then
    echo "✓ Redis found"
else
    echo "⚠️  Redis not found. Caching will use in-memory fallback."
    echo "Install: brew install redis (macOS) or sudo apt install redis (Linux)"
fi

echo ""
echo "======================================================"
echo "✅ Installation complete!"
echo ""
echo "Next steps:"
echo "1. Set up Supabase (see docs/SETUP.md)"
echo "2. Get Groq API key (console.groq.com)"
echo "3. Configure .env files"
echo "4. Run: python backend/manage.py runserver"
echo "5. Run: npm run dev (in frontend folder)"
echo ""
echo "Full guide: docs/SETUP.md"

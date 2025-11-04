# Recipe Management System - Setup Guide

This guide will walk you through setting up the Recipe Management System on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 20+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))
- **Redis** (optional for local development)
- **Tesseract OCR** (for image parsing)

## 1. Clone the Repository

```bash
git clone https://github.com/yourusername/recipe-management-system.git
cd recipe-management-system
```

## 2. Supabase Setup

### Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a free account
2. Click "New Project"
3. Choose a name, database password, and region
4. Wait for the project to be provisioned (usually 2-3 minutes)

### Enable pgvector Extension

1. Go to SQL Editor in your Supabase dashboard
2. Click "New Query"
3. Run the following SQL:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Run Database Migrations

Run the migration files in order from `database/migrations/supabase/`:

1. Copy the contents of `001_initial_schema.sql`
2. Paste into SQL Editor and run
3. Repeat for `002_add_rls_policies.sql`
4. Repeat for `003_add_indexes.sql`

### Get Your API Keys

1. Go to Settings → API in your Supabase dashboard
2. Copy the following:
   - **Project URL**: `https://your-project.supabase.co`
   - **anon public key**: For frontend
   - **service_role key**: For backend (keep secret!)

## 3. Groq API Setup

### Get a Free API Key

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for a free account
3. Go to API Keys section
4. Click "Create API Key"
5. Copy your API key (starts with `gsk_`)

**Note**: Free tier provides:
- 30 requests per minute
- 14,400 requests per day
- Access to all models

## 4. Tesseract OCR Setup

### Windows

1. Download the installer from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer (recommended path: `C:\Program Files\Tesseract-OCR`)
3. Add to system PATH:
   - Right-click "This PC" → Properties
   - Advanced system settings → Environment Variables
   - Add `C:\Program Files\Tesseract-OCR` to PATH

### macOS

```bash
brew install tesseract
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install tesseract-ocr
sudo apt install libtesseract-dev
```

### Verify Installation

```bash
tesseract --version
```

## 5. Backend Setup

### Create Virtual Environment

```bash
cd backend
python -m venv venv
```

### Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements/development.txt
```

### Configure Environment Variables

1. Copy the example file:
```bash
copy env.example .env  # Windows
# cp env.example .env  # macOS/Linux
```

2. Edit `.env` and add your keys:

```env
# Django
SECRET_KEY=your-random-secret-key-here
DEBUG=True

# Database (use Supabase connection string)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=your-supabase-db-password
DB_HOST=db.your-project-ref.supabase.co
DB_PORT=5432

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
SUPABASE_SERVICE_KEY=your-service-role-key

# Groq
GROQ_API_KEY=gsk_your-api-key-here

# Redis (optional for development)
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### Generate Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Run Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## 6. Frontend Setup

### Install Dependencies

```bash
cd frontend
npm install
```

### Configure Environment Variables

1. Copy the example file:
```bash
copy env.local.example .env.local  # Windows
# cp env.local.example .env.local  # macOS/Linux
```

2. Edit `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here

NEXT_PUBLIC_API_URL=http://localhost:8000

NEXT_PUBLIC_APP_NAME=Recipe Management System
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### Run Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:3000`

## 7. Optional: Redis Setup

### Windows

1. Download Redis from [GitHub](https://github.com/microsoftarchive/redis/releases)
2. Run the installer
3. Start Redis: `redis-server`

### macOS

```bash
brew install redis
brew services start redis
```

### Linux

```bash
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### Using Docker

```bash
docker run -d -p 6379:6379 redis:7-alpine
```

## 8. Verify Installation

### Backend Health Check

```bash
curl http://localhost:8000/api/
```

### Frontend

1. Open browser to `http://localhost:3000`
2. You should see the landing page
3. Register a new account
4. Login and access the dashboard

## 9. Load Sample Data

1. Register and login to create your user account
2. Get your user ID from Supabase dashboard (Auth → Users)
3. Open `database/seeds/sample_data.sql`
4. Replace `YOUR_USER_ID` with your actual user ID
5. Run the modified SQL in Supabase SQL Editor

## Troubleshooting

### Backend Issues

**"ModuleNotFoundError"**
```bash
pip install -r requirements/development.txt
```

**"Connection refused" (Database)**
- Verify Supabase credentials in `.env`
- Check if database is accessible
- Ensure pgvector extension is enabled

**"Groq API Error"**
- Verify API key is correct
- Check rate limits (30 requests/minute for free tier)

### Frontend Issues

**"Module not found"**
```bash
npm install
```

**"Network Error"**
- Ensure backend is running on port 8000
- Check NEXT_PUBLIC_API_URL in `.env.local`
- Verify CORS settings in Django

**Supabase Auth Issues**
- Ensure email confirmations are disabled in Supabase Auth settings (for development)
- Or check your email for confirmation link

### Tesseract Issues

**"TesseractNotFoundError"**
- Verify Tesseract is installed
- Check PATH environment variable
- Restart terminal after installation

## Next Steps

1. Explore the application
2. Add some ingredients
3. Upload recipes (text or images)
4. Chat with the AI assistant
5. Try the shopping list feature

For more detailed documentation, see:
- [API Documentation](./API_DOCUMENTATION.md)
- [Deployment Guide](./DEPLOYMENT.md)
- [Architecture Overview](./ARCHITECTURE.md)

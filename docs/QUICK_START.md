# Quick Start Guide - 5 Minutes

Get the Recipe Management System running in under 5 minutes!

## Prerequisites Check

```bash
python --version  # Should be 3.11+
node --version    # Should be 20+
```

## 1. Get the Code (30 seconds)

```bash
git clone https://github.com/yourusername/recipe-management-system.git
cd recipe-management-system
```

## 2. Supabase Setup (2 minutes)

1. Go to [supabase.com](https://supabase.com) → "New Project"
2. In SQL Editor, run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Copy `database/migrations/supabase/001_initial_schema.sql` content → Run in SQL Editor
4. Copy `002_add_rls_policies.sql` content → Run
5. Copy `003_add_indexes.sql` content → Run
6. Settings → API → Copy: URL and anon key

## 3. Groq API Key (1 minute)

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up (free)
3. Create API Key
4. Copy the key (starts with `gsk_`)

## 4. Backend Setup (1 minute)

```bash
cd backend
python -m venv venv
venv\Scripts\activate     # Windows
# source venv/bin/activate  # Mac/Linux

pip install -r requirements/development.txt

# Create .env file
echo SECRET_KEY=django-insecure-your-secret-key > .env
echo DEBUG=True >> .env
echo SUPABASE_URL=https://your-project.supabase.co >> .env
echo SUPABASE_KEY=your-anon-key >> .env
echo SUPABASE_SERVICE_KEY=your-service-key >> .env
echo GROQ_API_KEY=gsk_your-groq-key >> .env
echo REDIS_URL=redis://localhost:6379/0 >> .env

# Start server
python manage.py runserver
```

Backend running at: `http://localhost:8000`

## 5. Frontend Setup (1 minute)

**New terminal:**

```bash
cd frontend
npm install

# Create .env.local
echo NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co > .env.local
echo NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key >> .env.local
echo NEXT_PUBLIC_API_URL=http://localhost:8000 >> .env.local

npm run dev
```

Frontend running at: `http://localhost:3000`

## 6. Start Using! (30 seconds)

1. Open `http://localhost:3000`
2. Click "Create Account"
3. Register with your email
4. Login
5. Start adding ingredients!

## First Actions

### Add Your First Ingredient
1. Dashboard → Ingredients
2. Click "Add Ingredient"
3. Enter: Name: "Tomatoes", Quantity: 5, Unit: "pieces"
4. Save

### Upload Your First Recipe
1. Dashboard → Recipes
2. Click "Upload Recipe"
3. Paste a recipe or upload image
4. Watch AI parse it!

### Chat with AI
1. Dashboard → Chatbot
2. Type: "What can I cook?"
3. Get instant recommendations!

## Troubleshooting

**"Connection refused"**
- Ensure backend is running on port 8000
- Check .env files have correct values

**"Module not found"**
```bash
# Backend
pip install -r requirements/development.txt

# Frontend
npm install
```

**Tesseract OCR error**
- Install Tesseract (see SETUP.md)
- Or skip image upload for now

## Next Steps

- Read [SETUP.md](SETUP.md) for detailed setup
- Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for API details
- Review [ARCHITECTURE.md](ARCHITECTURE.md) to understand the system

## Need Help?

- Check docs/ folder
- Open GitHub issue
- Review error messages in console

---

**That's it!** You're ready to manage recipes like a pro! 🍳

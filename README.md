# Recipe Management System 🍳

A comprehensive full-stack application for managing kitchen ingredients, recipes, and meal planning with AI-powered recommendations.

## 🌟 Features

### Core Functionality
- **Ingredient Management**: Track kitchen inventory with expiry dates and categories
- **Recipe Storage**: Parse and store recipes from text or images using AI
- **Smart Recommendations**: Get recipe suggestions based on available ingredients
- **Shopping List**: Manage shopping needs with recipe integration
- **AI Chatbot**: Natural language interface for recipe discovery and cooking help

### Technical Highlights
- **Full-Stack Architecture**: Next.js 14 (Frontend) + Django 5 (Backend)
- **AI Integration**: Groq LLM for text parsing and recommendations
- **OCR Support**: Tesseract for recipe image extraction
- **Vector Search**: pgvector for semantic recipe search
- **Real-time Updates**: Supabase for live data synchronization
- **Modern UI**: Tailwind CSS + shadcn/ui components

## 🏗️ Architecture

```
Frontend (Next.js) ←→ API Gateway (Django REST) ←→ Backend Services
                                                         ↓
                                              Database (Supabase/PostgreSQL)
                                                         ↓
                                              External Services (Groq, OCR)
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL (via Supabase)
- Redis (for caching)
- Tesseract OCR

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/recipe-management-system.git
cd recipe-management-system
```

### 2. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On macOS/Linux

pip install -r requirements/development.txt

# Copy and configure environment variables
copy env.example .env
# Edit .env with your settings

# Run migrations (after Supabase setup)
python manage.py migrate
python manage.py runserver
```

### 3. Frontend Setup

```bash
cd frontend
npm install

# Copy and configure environment variables
copy env.local.example .env.local
# Edit .env.local with your settings

npm run dev
```

### 4. Supabase Setup

1. Create a project at [supabase.com](https://supabase.com)
2. Enable pgvector extension in SQL Editor:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Run migration files from `database/migrations/supabase/` in order
4. Copy your project URL and keys to `.env` files

### 5. Groq API Setup

1. Get a free API key from [console.groq.com](https://console.groq.com)
2. Add to backend `.env`: `GROQ_API_KEY=your-key-here`

## 📱 Usage

### Adding Ingredients
1. Navigate to Ingredients page
2. Click "Add Ingredient"
3. Fill in details (name, quantity, expiry date)
4. Save to inventory

### Uploading Recipes
- **Text**: Paste recipe text and click "Parse"
- **Image**: Upload recipe photo for OCR extraction
- **Batch**: Import multiple recipes from a text file

### Getting Recommendations
1. Go to Chatbot
2. Ask questions like:
   - "What can I make for dinner?"
   - "I want something sweet"
   - "Quick Italian recipes"

### Shopping List
- Add items manually
- Generate from recipe ingredients
- Mark as purchased
- Transfer to inventory

## 🛠️ Development

### Project Structure
```
recipe-management-system/
├── backend/           # Django REST API
├── frontend/          # Next.js application
├── database/          # Migration files
├── ml_models/         # ML/AI utilities
├── scripts/           # Deployment scripts
└── docs/             # Documentation
```

### Running Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

### Docker Development
```bash
docker-compose up -d
```

## 📊 API Documentation

### Authentication
- `POST /api/auth/register/` - Create account
- `POST /api/auth/login/` - Login
- `POST /api/auth/logout/` - Logout

### Ingredients
- `GET /api/ingredients/` - List ingredients
- `POST /api/ingredients/` - Add ingredient
- `PATCH /api/ingredients/{id}/` - Update
- `DELETE /api/ingredients/{id}/` - Remove

### Recipes
- `GET /api/recipes/` - Browse recipes
- `POST /api/recipes/parse-text/` - Parse text recipe
- `POST /api/recipes/parse-image/` - Parse image recipe
- `GET /api/recipes/search/` - Search recipes

### Chatbot
- `POST /api/chatbot/chat/` - Send message
- `POST /api/chatbot/recommend/` - Get recommendations
- `POST /api/chatbot/meal-plan/` - Generate meal plan

## 🚢 Deployment

### Backend (Railway/Render)
1. Configure environment variables
2. Set build command: `pip install -r requirements/production.txt`
3. Set start command: `gunicorn config.wsgi:application`

### Frontend (Vercel)
1. Import GitHub repository
2. Configure environment variables
3. Deploy with automatic builds

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Groq for providing free LLM API
- Supabase for database hosting
- shadcn/ui for beautiful components
- The open-source community

## 📞 Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/recipe-management-system/issues)
- Documentation: Check the `docs/` folder

---

Built with ❤️ for home cooks everywhere!
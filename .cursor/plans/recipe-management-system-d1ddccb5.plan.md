<!-- d1ddccb5-8320-4205-a095-0d2ee3e341df df27c429-e891-4cfe-b359-83a38b795fc3 -->
# Recipe Management System - Full Stack Implementation

## Phase 1: Project Setup & Configuration

### 1.1 Backend Foundation (Django)

- Create Django project structure with modular apps:
  - `backend/config/` - Settings split by environment (base, dev, prod)
  - `backend/apps/authentication/` - JWT auth with Supabase
  - `backend/apps/ingredients/` - Ingredient CRUD operations
  - `backend/apps/recipes/` - Recipe parsing and storage
  - `backend/apps/chatbot/` - LLM integration with Groq
  - `backend/apps/storage/` - Supabase storage integration
  - `backend/apps/common/` - Shared utilities

- Create `requirements/base.txt` with:
  - Django 5.x, djangorestframework, djangorestframework-simplejwt
  - supabase, psycopg2-binary, python-dotenv
  - groq, langchain, sentence-transformers
  - pytesseract, Pillow, pdf2image
  - celery, redis, django-cors-headers

- Setup `.env.example` with all required environment variables:
  - `SUPABASE_URL`, `SUPABASE_KEY`, `SUPABASE_SERVICE_KEY`
  - `GROQ_API_KEY`, `DATABASE_URL`
  - `REDIS_URL`, `SECRET_KEY`, `DEBUG`

### 1.2 Frontend Foundation (Next.js)

- Initialize Next.js 14 app with TypeScript:
  - App router structure with `(auth)` and `(dashboard)` groups
  - shadcn/ui components setup with Tailwind CSS
  - Supabase client configuration (browser & server)

- Create `frontend/src/lib/supabase/` for:
  - `client.ts` - Browser Supabase client
  - `server.ts` - Server-side Supabase client
  - `middleware.ts` - Auth middleware

- Setup `.env.local.example` with:
  - `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - `NEXT_PUBLIC_API_URL` (Django backend)

### 1.3 Database Schema (Supabase)

Create migration files in `database/migrations/supabase/`:

**001_initial_schema.sql**:

```sql
-- Users table (managed by Supabase Auth)
-- Ingredients table
CREATE TABLE ingredients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  quantity DECIMAL(10,2),
  unit VARCHAR(50),
  category VARCHAR(100),
  expiry_date DATE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Recipes table
CREATE TABLE recipes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  title VARCHAR(500) NOT NULL,
  description TEXT,
  ingredients JSONB NOT NULL,
  instructions TEXT,
  cuisine_type VARCHAR(100),
  taste_profile VARCHAR(100),
  preparation_time INTEGER,
  cooking_time INTEGER,
  servings INTEGER,
  difficulty VARCHAR(50),
  image_url TEXT,
  source_type VARCHAR(50),
  embedding VECTOR(384),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Shopping list table
CREATE TABLE shopping_list (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  ingredient_name VARCHAR(255) NOT NULL,
  quantity DECIMAL(10,2),
  unit VARCHAR(50),
  purchased BOOLEAN DEFAULT FALSE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat history table
CREATE TABLE chat_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  message TEXT NOT NULL,
  response TEXT NOT NULL,
  context JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

**002_add_rls_policies.sql** - Row Level Security:

- Enable RLS on all tables
- Policies: Users can only access their own data

**003_add_indexes.sql**:

- Indexes on `user_id`, `created_at`, vector similarity search

### 1.4 Docker Configuration

- `backend/Dockerfile` - Multi-stage Django build with Tesseract
- `frontend/Dockerfile` - Next.js optimized build
- `docker-compose.yml` - Full stack with Redis, services networking

## Phase 2: Backend API Development

### 2.1 Authentication System

File: `backend/apps/authentication/views.py`

- JWT token generation with Supabase user validation
- Register, login, logout, token refresh endpoints
- User profile management

### 2.2 Ingredient Management API

Files: `backend/apps/ingredients/models.py`, `views.py`, `serializers.py`

Key endpoints:

- `POST /api/ingredients/` - Add ingredient
- `GET /api/ingredients/` - List all (with filters: category, expiring soon)
- `PATCH /api/ingredients/{id}/` - Update quantity/notes
- `DELETE /api/ingredients/{id}/` - Remove ingredient
- `POST /api/ingredients/bulk-update/` - Update after shopping/cooking
- `GET /api/ingredients/categories/` - Get unique categories

### 2.3 Recipe Parsing Service

Files: `backend/apps/recipes/services.py`, `parsers/text_parser.py`, `parsers/image_parser.py`

**Text Parser** (`text_parser.py`):

- Use Groq LLM to parse unstructured recipe text
- Extract: title, ingredients, instructions, metadata
- Structured output with Pydantic models

**Image Parser** (`image_parser.py`):

- Tesseract OCR to extract text from recipe images
- Preprocessing: grayscale, threshold, noise removal
- Pass extracted text to text parser

**Recipe Service** (`services.py`):

- Generate embeddings using `sentence-transformers`
- Store recipe with embedding in Supabase (pgvector)
- Batch processing for `my_fav_recipes.txt`

Endpoints:

- `POST /api/recipes/parse-text/` - Parse text recipe
- `POST /api/recipes/parse-image/` - Upload & parse recipe image
- `POST /api/recipes/batch-import/` - Process combined text file
- `GET /api/recipes/` - List recipes (with filters)
- `GET /api/recipes/{id}/` - Recipe detail
- `DELETE /api/recipes/{id}/` - Remove recipe

### 2.4 Shopping List API

Files: `backend/apps/recipes/shopping_views.py`

Endpoints:

- `POST /api/shopping-list/` - Add item
- `GET /api/shopping-list/` - Get list
- `PATCH /api/shopping-list/{id}/toggle/` - Mark purchased
- `POST /api/shopping-list/generate-from-recipe/{recipe_id}/` - Auto-generate from recipe

### 2.5 LLM Chatbot Service

Files: `backend/apps/chatbot/services/llm_service.py`, `recommendation_engine.py`, `prompts.py`

**LLM Service** (`llm_service.py`):

- Groq API integration (llama-3.1-70b or mixtral)
- Streaming response support
- Context window management

**Recommendation Engine** (`recommendation_engine.py`):

- Semantic search using pgvector (cosine similarity)
- Filter recipes by available ingredients
- Scoring system: ingredient match % + user preferences
- Generate missing ingredients list

**Prompts** (`prompts.py`):

- System prompt with role definition
- Few-shot examples for recipe recommendations
- Structured output format

Endpoints:

- `POST /api/chatbot/chat/` - Send message, get recommendation
- `GET /api/chatbot/history/` - Get chat history
- `POST /api/chatbot/recommend/` - Get recipe suggestions based on query

Key Features:

- Parse user intent ("I want something sweet", "Quick dinner")
- Query available ingredients from DB
- Vector search recipes with filters (taste, cuisine, time)
- Return matched recipes with missing ingredients
- Natural language explanation

## Phase 3: Frontend Development

### 3.1 Authentication Pages

Files: `frontend/src/app/(auth)/login/page.tsx`, `register/page.tsx`

- Login/Register forms with Supabase Auth
- JWT token storage in httpOnly cookies
- Protected route middleware

### 3.2 Dashboard Layout

File: `frontend/src/app/(dashboard)/layout.tsx`

- Sidebar navigation (Dashboard, Ingredients, Recipes, Chatbot, Shopping)
- User profile dropdown
- Responsive mobile menu

### 3.3 Ingredients Management

Files: `frontend/src/app/(dashboard)/ingredients/page.tsx`, components

Features:

- Data table with sorting, filtering, search
- Add ingredient modal with form validation
- Quick edit quantity inline
- Category filters, expiry warnings
- Bulk import from CSV

### 3.4 Recipe Browser

Files: `frontend/src/app/(dashboard)/recipes/page.tsx`, `[id]/page.tsx`

Features:

- Grid/list view toggle
- Recipe cards with images
- Filters: cuisine, taste, preparation time
- Recipe detail modal with ingredients checklist
- Upload new recipe (text/image)
- Batch import interface for `my_fav_recipes.txt`

### 3.5 Chatbot Interface

File: `frontend/src/app/(dashboard)/chatbot/page.tsx`

Features:

- Chat UI with message history
- Streaming responses
- Recipe cards in chat (clickable)
- Quick suggestions chips ("Quick meal", "Dessert", "Italian")
- Ingredient availability indicator
- Add missing ingredients to shopping list

### 3.6 Shopping List

File: `frontend/src/app/(dashboard)/shopping-list/page.tsx`

Features:

- Checklist UI with toggle
- Add items manually or from recipes
- Group by category
- "Add to Ingredients" after purchase

### 3.7 Shared Components

`frontend/src/components/`:

- `ui/` - shadcn components (Button, Input, Card, Dialog, etc.)
- `ingredients/IngredientForm.tsx`, `IngredientTable.tsx`
- `recipes/RecipeCard.tsx`, `RecipeUploadModal.tsx`
- `chatbot/ChatMessage.tsx`, `RecipeRecommendation.tsx`
- `common/Navbar.tsx`, `Sidebar.tsx`, `LoadingSpinner.tsx`

## Phase 4: Integration & Testing

### 4.1 API Client Setup

File: `frontend/src/lib/api/client.ts`

- Axios instance with interceptors
- JWT token refresh logic
- Error handling with toast notifications

### 4.2 Setup Guides

Create `docs/SETUP.md`:

1. **Supabase Setup**:

   - Create project at supabase.com
   - Enable pgvector extension
   - Run migration SQL files
   - Copy API keys to .env

2. **Groq API Setup**:

   - Register at console.groq.com
   - Generate API key (free tier: 30 requests/min)
   - Add to .env

3. **Tesseract Installation**:

   - Windows: Download installer
   - Mac: `brew install tesseract`
   - Linux: `apt-get install tesseract-ocr`

4. **Local Development**:

   - Backend: `pip install -r requirements/development.txt`
   - Frontend: `npm install`
   - Run: `python manage.py runserver` & `npm run dev`

### 4.3 Seed Data

File: `database/seeds/sample_data.sql`

- Sample ingredients (20-30 common items)
- Sample recipes (10-15 diverse cuisines)
- Pre-generated embeddings

## Phase 5: Deployment Configuration

### 5.1 Backend Deployment (Railway/Render)

Files:

- `railway.json` or `render.yaml`
- `scripts/deploy_backend.sh`
- Production settings with environment variables
- Gunicorn + WhiteNoise for static files

### 5.2 Frontend Deployment (Vercel)

Files:

- `vercel.json` with build configuration
- `scripts/deploy_frontend.sh`
- Environment variables setup guide

### 5.3 CI/CD Pipeline

File: `.github/workflows/ci.yml`

- Run tests on PR
- Linting (pylint, eslint)
- Type checking (mypy, tsc)
- Security scan (bandit, npm audit)

### 5.4 Documentation

Files:

- `README.md` - Project overview, features, quick start
- `docs/API_DOCUMENTATION.md` - All endpoints with examples
- `docs/DEPLOYMENT.md` - Step-by-step deployment guide
- `docs/ARCHITECTURE.md` - System design explanation
- `.env.example` files with all variables

## Key Implementation Details

**Vector Search Strategy**:

- Generate embeddings for recipes during parsing
- Store in pgvector column
- Query: `ORDER BY embedding <=> query_embedding LIMIT 5`

**Large File Handling** (`my_fav_recipes.txt`):

- Chunking: Split by recipe markers (## Title, ---, etc.)
- Async processing with Celery tasks
- Progress tracking endpoint
- Store raw text + parsed structured data

**Ingredient Matching Algorithm**:

- Normalize names (lowercase, singular form)
- Fuzzy matching with threshold (e.g., "tomatos" → "tomato")
- Calculate match percentage
- Suggest substitutions for missing ingredients

**Caching Strategy**:

- Redis for: Embeddings, frequent recipe queries, chat context
- Cache TTL: 1 hour for recipes, 15 min for chat

**Error Handling**:

- Graceful degradation: If Groq fails, return cached/top recipes
- OCR fallback: If image quality poor, ask user for manual input
- Rate limiting: Handle Groq API limits with exponential backoff

### To-dos

- [ ] Create project folder structure, initialize Django backend and Next.js frontend with all necessary configuration files
- [ ] Create requirements files for Django and package.json for Next.js with all dependencies
- [ ] Write Supabase migration SQL files for ingredients, recipes, shopping list, and chat history tables with RLS policies
- [ ] Create Django apps (authentication, ingredients, recipes, chatbot, storage) with models, serializers, and views
- [ ] Build ingredient management API with CRUD operations, filtering, and bulk update endpoints
- [ ] Create text parser using Groq LLM and image parser using Tesseract OCR for recipe extraction
- [ ] Build recipe API with parsing endpoints, embedding generation, and vector search integration
- [ ] Integrate Groq API, build recommendation engine with vector search, create chat endpoints
- [ ] Create shopping list API with CRUD operations and recipe integration
- [ ] Initialize Next.js with app router, setup Supabase client, configure Tailwind and shadcn/ui
- [ ] Create login and register pages with Supabase Auth integration
- [ ] Create dashboard layout with sidebar navigation and protected routes
- [ ] Create ingredients management page with table, forms, and filtering
- [ ] Create recipe browser with grid view, filters, upload modal, and detail view
- [ ] Create chatbot interface with message history, streaming, and recipe recommendations
- [ ] Create shopping list page with checklist and recipe integration
- [ ] Create Dockerfiles for backend and frontend, docker-compose.yml with Redis
- [ ] Write comprehensive setup guides for Supabase, Groq API, Tesseract, and local development
- [ ] Generate sample data SQL with ingredients and recipes for testing
- [ ] Create deployment configurations for Vercel, Railway/Render, and CI/CD pipeline
- [ ] Document all API endpoints with request/response examples
- [ ] Test complete flow: add ingredients, upload recipes, chat for recommendations, manage shopping list
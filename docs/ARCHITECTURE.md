# System Architecture

## Overview

The Recipe Management System follows a modern, scalable architecture with clear separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer (Next.js)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Dashboard  │  │   Chatbot    │  │  Ingredients │     │
│  │     Page     │  │   Interface  │  │  Management  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↕ HTTPS/WSS
┌─────────────────────────────────────────────────────────────┐
│                  API Gateway & Auth Layer                    │
│              (Django REST Framework + JWT)                   │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    Backend Services (Django)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Ingredient  │  │    Recipe    │  │   LLM/Chat   │     │
│  │   Service    │  │   Service    │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │     OCR      │  │  Vector DB   │  │   Storage    │     │
│  │   Service    │  │   Service    │  │   Service    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer (Supabase)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  PostgreSQL  │  │    Storage   │  │  Realtime    │     │
│  │   Database   │  │   (S3-like)  │  │  Subscr.     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                            ↕
┌─────────────────────────────────────────────────────────────┐
│                    External Services                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │     LLM      │  │    Vector    │  │     OCR      │     │
│  │    (Groq)    │  │   (pgvector) │  │  (Tesseract) │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS + shadcn/ui
- **State Management**: React Hooks + Axios
- **Authentication**: Supabase Auth
- **Deployment**: Vercel

### Backend
- **Framework**: Django 5.0 + Django REST Framework
- **Language**: Python 3.11
- **Authentication**: JWT + Supabase integration
- **Task Queue**: Celery with Redis
- **Deployment**: Railway/Render

### Database & Storage
- **Database**: PostgreSQL (Supabase)
- **Vector Search**: pgvector extension
- **File Storage**: Supabase Storage
- **Caching**: Redis

### AI/ML Services
- **LLM**: Groq API (Llama 3.1 70B)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **OCR**: Tesseract

## Component Breakdown

### Frontend Components

#### Authentication Layer
- Login/Register pages with Supabase
- JWT token management
- Protected route middleware
- Session refresh logic

#### Dashboard
- Overview statistics
- Quick action cards
- Navigation sidebar
- User profile menu

#### Feature Modules
1. **Ingredients Management**
   - CRUD operations
   - CSV import/export
   - Expiry tracking
   - Category filtering

2. **Recipe Browser**
   - Grid/List view
   - Text/Image upload
   - Batch import
   - Favorite management

3. **Chatbot Interface**
   - Real-time chat
   - Recipe recommendations
   - Ingredient analysis
   - Meal planning

4. **Shopping List**
   - Item management
   - Recipe integration
   - Purchase tracking
   - Inventory transfer

### Backend Services

#### Core Services

**Authentication Service**
- User registration/login
- JWT token generation
- Supabase Auth integration
- Profile management

**Ingredient Service**
- CRUD operations
- Normalization logic
- Availability checking
- Expiry notifications

**Recipe Service**
- Text parsing (LLM)
- Image parsing (OCR)
- Embedding generation
- Batch processing
- Vector search

**Chatbot Service**
- Natural language processing
- Context management
- Recipe recommendations
- Meal plan generation

**Storage Service**
- File upload to Supabase
- Image optimization
- URL generation
- Access control

#### Background Tasks (Celery)

- Batch recipe import
- Embedding generation
- Email notifications
- Cleanup jobs

## Data Flow

### Recipe Upload Flow (Text)

```
User Input (Text)
    ↓
Frontend: Upload Component
    ↓
Backend: Parse Text Endpoint
    ↓
Groq LLM: Extract Structure
    ↓
Backend: Generate Embedding
    ↓
Supabase: Store Recipe
    ↓
Frontend: Display Success
```

### Recipe Upload Flow (Image)

```
User Input (Image)
    ↓
Frontend: Upload Component
    ↓
Backend: Parse Image Endpoint
    ↓
Tesseract OCR: Extract Text
    ↓
Groq LLM: Parse Structure
    ↓
Backend: Generate Embedding
    ↓
Supabase: Store Recipe + Image
    ↓
Frontend: Display Success
```

### Chatbot Recommendation Flow

```
User Message
    ↓
Frontend: Chat Interface
    ↓
Backend: Chat Endpoint
    ↓
┌───────────────────────┐
│ 1. Fetch User's       │
│    Ingredients        │
│ 2. Generate Query     │
│    Embedding          │
│ 3. Vector Search      │
│    (pgvector)         │
│ 4. Filter by          │
│    Ingredients        │
│ 5. Score Recipes      │
└───────────────────────┘
    ↓
Groq LLM: Generate Natural Response
    ↓
Backend: Store Chat History
    ↓
Frontend: Display Response + Recipes
```

## Database Schema

### Core Tables

**ingredients**
- Primary storage for user inventory
- Includes expiry tracking
- Category-based organization
- Full-text search support

**recipes**
- Stores parsed recipe data
- JSONB for flexible ingredient storage
- Vector embeddings for semantic search
- Full-text search on title/description

**shopping_list**
- Links to recipes
- Purchase tracking
- Easy transfer to ingredients

**chat_history**
- Conversation persistence
- Context preservation
- Recommendation tracking

### Relationships

```
users (Supabase Auth)
  ↓
  ├─→ ingredients (one-to-many)
  ├─→ recipes (one-to-many)
  ├─→ shopping_list (one-to-many)
  ├─→ chat_history (one-to-many)
  └─→ recipe_favorites (many-to-many with recipes)
```

## Security Architecture

### Authentication Flow
1. User registers → Supabase Auth
2. Login → JWT tokens generated
3. Frontend stores tokens securely
4. API requests include JWT
5. Backend validates tokens
6. RLS policies enforce data isolation

### Data Security
- Row Level Security (RLS) on all tables
- User can only access own data
- Service role for backend operations
- Encrypted connections (HTTPS/WSS)

### API Security
- Rate limiting on endpoints
- CORS configuration
- Input validation
- SQL injection prevention
- XSS protection

## Performance Optimization

### Caching Strategy
- **Redis caching** for:
  - Recipe embeddings
  - Frequent queries
  - Chat context
  - User sessions

### Database Optimization
- Indexes on frequently queried fields
- Vector indexes for similarity search
- Composite indexes for complex queries
- Connection pooling

### Frontend Optimization
- Server-side rendering (SSR)
- Image optimization
- Code splitting
- CDN delivery (Vercel)

## Scalability Considerations

### Horizontal Scaling
- **Frontend**: Vercel auto-scales
- **Backend**: Railway/Render auto-scales
- **Database**: Supabase connection pooling

### Vertical Scaling
- Upgrade server resources as needed
- Optimize queries for large datasets
- Implement pagination everywhere

### Future Enhancements
- Redis cluster for high availability
- Database read replicas
- CDN for recipe images
- Microservices architecture

## Monitoring & Logging

### Application Monitoring
- **Sentry**: Error tracking
- **Railway/Render**: Performance metrics
- **Vercel**: Analytics

### Logging Strategy
- Structured logging (JSON)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized log aggregation
- Searchable logs

## Development Workflow

```
Developer
    ↓
Local Development (Docker Compose)
    ↓
Git Push → GitHub
    ↓
CI Pipeline (GitHub Actions)
    ├─→ Run Tests
    ├─→ Linting
    ├─→ Security Scan
    └─→ Build Verification
    ↓
Merge to Main
    ↓
CD Pipeline (GitHub Actions)
    ├─→ Deploy Backend (Railway)
    └─→ Deploy Frontend (Vercel)
    ↓
Production
```

## API Design Principles

1. **RESTful**: Standard HTTP methods
2. **Consistent**: Uniform response format
3. **Versioned**: Future-proof API
4. **Documented**: OpenAPI/Swagger
5. **Secure**: Authentication required
6. **Validated**: Input validation
7. **Paginated**: Large result sets
8. **Filtered**: Flexible queries

## Error Handling

### Frontend
- Toast notifications for user feedback
- Error boundaries for crash recovery
- Retry logic for failed requests
- Graceful degradation

### Backend
- Custom exception classes
- Global exception handler
- Detailed error messages (dev)
- Generic messages (prod)
- Error logging to Sentry

## Testing Strategy

### Backend Testing
- **Unit Tests**: Individual functions
- **Integration Tests**: API endpoints
- **Service Tests**: Business logic
- **Database Tests**: ORM queries

### Frontend Testing
- **Component Tests**: UI components
- **Integration Tests**: Page flows
- **E2E Tests**: User journeys
- **Visual Regression**: UI changes

## Configuration Management

### Environment-based Settings
- **Development**: Debug enabled, local services
- **Testing**: Isolated test database
- **Production**: Optimized, secure settings

### Secret Management
- Environment variables
- Never commit secrets
- Use .env files locally
- Platform secrets in production

## Future Architecture Improvements

1. **Microservices**: Split into smaller services
2. **Event-Driven**: Use message queues
3. **GraphQL**: Alternative API layer
4. **Real-time**: WebSocket for live updates
5. **Multi-tenancy**: Support multiple organizations
6. **Mobile Apps**: React Native clients

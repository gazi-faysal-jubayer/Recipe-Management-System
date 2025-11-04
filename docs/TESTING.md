# Testing Guide

This document describes how to test the Recipe Management System.

## Testing Strategy

### Backend Testing

#### Unit Tests

Test individual functions and methods:

```bash
cd backend
pytest tests/unit/ -v
```

#### Integration Tests

Test API endpoints and database operations:

```bash
pytest tests/integration/ -v
```

#### Coverage Report

```bash
pytest --cov=apps --cov-report=html
# Open htmlcov/index.html in browser
```

### Frontend Testing

#### Component Tests

```bash
cd frontend
npm test
```

#### Type Checking

```bash
npm run type-check
```

#### Build Test

```bash
npm run build
```

## Manual Testing Checklist

### 1. Authentication Flow

- [ ] Register new account
  - Go to `/register`
  - Fill in email, password, full name
  - Submit form
  - Check email for confirmation (if enabled)
  - Verify success message

- [ ] Login
  - Go to `/login`
  - Enter credentials
  - Verify redirect to dashboard
  - Check user info in navbar

- [ ] Logout
  - Click user dropdown
  - Click logout
  - Verify redirect to login page

### 2. Ingredient Management

- [ ] Add ingredient manually
  - Navigate to `/ingredients`
  - Click "Add Ingredient"
  - Fill in name, quantity, unit, category
  - Set expiry date
  - Save
  - Verify appears in list

- [ ] Edit ingredient
  - Click edit on an ingredient
  - Modify quantity
  - Save
  - Verify changes

- [ ] Delete ingredient
  - Click delete
  - Confirm deletion
  - Verify removed from list

- [ ] Filter ingredients
  - Test search by name
  - Test "Expiring Soon" filter
  - Test category filter

- [ ] Import CSV
  - Prepare CSV file with ingredients
  - Click "Import CSV"
  - Upload file
  - Verify import success

### 3. Recipe Management

- [ ] Add recipe manually
  - Navigate to `/recipes`
  - Click "Add Recipe"
  - Fill in all fields
  - Add ingredients (one per line)
  - Add instructions
  - Save
  - Verify appears in grid

- [ ] Parse recipe from text
  - Click "Upload Recipe"
  - Select "Text" tab
  - Paste recipe text
  - Click "Parse Recipe"
  - Verify AI extracts correct data
  - Check ingredients and instructions

- [ ] Parse recipe from image
  - Click "Upload Recipe"
  - Select "Image" tab
  - Upload recipe image (clear text)
  - Click "Extract Recipe"
  - Verify OCR extracts text
  - Verify AI parses correctly

- [ ] Batch import recipes
  - Prepare text file with multiple recipes
  - Use batch import feature
  - Monitor progress
  - Verify all recipes imported

- [ ] Favorite recipe
  - Click heart icon on recipe
  - Verify turns red
  - Check favorites section

- [ ] Search recipes
  - Use search bar
  - Test filters (cuisine, difficulty)
  - Verify results

### 4. Chatbot Interaction

- [ ] Basic chat
  - Navigate to `/chatbot`
  - Send message: "What can I cook?"
  - Verify AI responds
  - Check recommendations appear

- [ ] Specific requests
  - Ask: "I want something sweet"
  - Verify sweet recipes recommended
  - Ask: "Quick dinner ideas"
  - Verify quick recipes shown

- [ ] Ingredient-based recommendations
  - Ask: "What can I make with pasta and tomatoes?"
  - Verify relevant recipes
  - Check ingredient match percentages

- [ ] View chat history
  - Verify previous messages shown
  - Test scrolling through history

### 5. Shopping List

- [ ] Add item manually
  - Navigate to `/shopping-list`
  - Click "Add Item"
  - Enter ingredient name, quantity
  - Save
  - Verify in unpurchased list

- [ ] Add from recipe
  - View a recipe
  - Click "Add to Shopping List"
  - Verify all ingredients added

- [ ] Mark as purchased
  - Click checkbox on item
  - Verify moves to purchased section

- [ ] Transfer to inventory
  - Mark items as purchased
  - Click "Add to Inventory"
  - Verify items move to ingredients
  - Verify removed from shopping list

- [ ] Clear purchased
  - Click "Clear Purchased"
  - Confirm action
  - Verify purchased items removed

## API Testing

### Using cURL

#### Register
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "confirm_password": "testpass123"
  }'
```

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

#### Add Ingredient (with token)
```bash
curl -X POST http://localhost:8000/api/ingredients/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Tomatoes",
    "quantity": 5,
    "unit": "pieces",
    "category": "Vegetables"
  }'
```

### Using Postman/Insomnia

1. Import API documentation from `/api/swagger/`
2. Set base URL to `http://localhost:8000`
3. Configure Authorization header with Bearer token
4. Test all endpoints

## Performance Testing

### Load Testing

```bash
# Install Apache Bench
# Windows: Download from Apache website
# Mac: brew install ab
# Linux: apt install apache2-utils

# Test API endpoint
ab -n 1000 -c 10 -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/ingredients/
```

### Database Performance

```sql
-- Check query performance
EXPLAIN ANALYZE
SELECT * FROM recipes
WHERE embedding <=> '[0.1, 0.2, ...]'::vector
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 10;

-- Check index usage
SELECT
  schemaname,
  tablename,
  indexname,
  idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

## Error Scenarios

### Test Error Handling

- [ ] Invalid credentials
- [ ] Expired token
- [ ] Malformed data
- [ ] File too large
- [ ] Network timeout
- [ ] Database connection loss
- [ ] Groq API rate limit
- [ ] Invalid image format

### Expected Behaviors

- Clear error messages
- Graceful degradation
- User-friendly feedback
- Automatic retry (where appropriate)
- Fallback mechanisms

## Security Testing

### Basic Security Checks

- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CSRF tokens
- [ ] Rate limiting works
- [ ] RLS policies enforce access
- [ ] File upload validation
- [ ] Password strength requirements

### Tools

```bash
# Backend security scan
bandit -r backend/apps/

# Frontend dependency audit
cd frontend
npm audit

# Check for sensitive data in git
git secrets --scan
```

## Browser Compatibility

Test in:
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile browsers

## Accessibility Testing

- [ ] Keyboard navigation
- [ ] Screen reader compatibility
- [ ] Color contrast
- [ ] Form labels
- [ ] ARIA attributes

## Continuous Integration

Tests run automatically on:
- Every push to `develop` or `main`
- Every pull request
- Before deployment

View results in GitHub Actions tab.

## Reporting Issues

When reporting bugs:
1. Steps to reproduce
2. Expected vs actual behavior
3. Screenshots/videos
4. Browser/OS information
5. Error messages
6. Network requests (if applicable)

## Test Data

Use the sample data from:
- `database/seeds/sample_data.sql`
- Or create test fixtures in `backend/tests/fixtures/`

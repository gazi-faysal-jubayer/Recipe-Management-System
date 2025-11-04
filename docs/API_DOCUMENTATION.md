# API Documentation

Base URL: `http://localhost:8000` (Development) or `https://your-backend.railway.app` (Production)

All API endpoints require authentication unless otherwise specified. Include the JWT token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

## Authentication

### Register User

**POST** `/api/auth/register/`

Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "confirm_password": "securepassword123",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Registration successful",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe",
      "date_joined": "2024-01-15T10:30:00Z"
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
  }
}
```

### Login

**POST** `/api/auth/login/`

Authenticate user and receive tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "user": {
      "id": 1,
      "email": "user@example.com",
      "full_name": "John Doe"
    },
    "tokens": {
      "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
      "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    },
    "supabase_session": {
      "access_token": "...",
      "refresh_token": "..."
    }
  }
}
```

### Get Profile

**GET** `/api/auth/profile/`

Get current user's profile.

**Response (200):**
```json
{
  "success": true,
  "message": "Profile retrieved successfully",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "date_joined": "2024-01-15T10:30:00Z"
  }
}
```

## Ingredients

### List Ingredients

**GET** `/api/ingredients/`

Get user's ingredients with optional filters.

**Query Parameters:**
- `category` (string): Filter by category
- `expiring` (boolean): Show only expiring soon
- `search` (string): Search by name
- `ordering` (string): Sort field (e.g., `-created_at`, `name`)

**Example:**
```
GET /api/ingredients/?category=Vegetables&expiring=true
```

**Response (200):**
```json
{
  "success": true,
  "message": "Success",
  "data": [
    {
      "id": "uuid",
      "name": "Tomatoes",
      "quantity": 5,
      "unit": "pieces",
      "category": "Vegetables",
      "expiry_date": "2024-01-22",
      "notes": "Fresh from market",
      "is_expiring_soon": true,
      "is_expired": false,
      "days_until_expiry": 3,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### Add Ingredient

**POST** `/api/ingredients/`

Add a new ingredient.

**Request:**
```json
{
  "name": "Carrots",
  "quantity": 10,
  "unit": "pieces",
  "category": "Vegetables",
  "expiry_date": "2024-01-25",
  "notes": "Organic"
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Ingredient added successfully",
  "data": {
    "id": "uuid",
    "name": "Carrots",
    ...
  }
}
```

### Update Ingredient

**PATCH** `/api/ingredients/{id}/`

Update an existing ingredient.

**Request:**
```json
{
  "quantity": 8,
  "notes": "Used 2 for soup"
}
```

### Delete Ingredient

**DELETE** `/api/ingredients/{id}/`

Delete an ingredient.

**Response (204):**
```json
{
  "success": true,
  "message": "Ingredient deleted successfully"
}
```

### Bulk Update Ingredients

**POST** `/api/ingredients/bulk-update/`

Add, update, or delete multiple ingredients.

**Request (Add):**
```json
{
  "operation": "add",
  "ingredients": [
    {"name": "Apples", "quantity": 6, "unit": "pieces"},
    {"name": "Bananas", "quantity": 4, "unit": "pieces"}
  ]
}
```

**Request (Update):**
```json
{
  "operation": "update",
  "ingredients": [
    {"id": "uuid1", "quantity": 3},
    {"id": "uuid2", "quantity": 2}
  ]
}
```

### Get Categories

**GET** `/api/ingredients/categories/`

Get available ingredient categories.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "user_categories": ["Vegetables", "Fruits", "Dairy"],
    "predefined_categories": [
      {"id": "uuid", "name": "Vegetables", "display_order": 1}
    ]
  }
}
```

## Recipes

### List Recipes

**GET** `/api/recipes/`

Get user's recipes.

**Query Parameters:**
- `cuisine_type` (string): Filter by cuisine
- `difficulty` (string): easy, medium, or hard
- `search` (string): Search in title/description
- `ordering` (string): Sort field

**Response (200):**
```json
{
  "results": [
    {
      "id": "uuid",
      "title": "Spaghetti Carbonara",
      "description": "Classic Italian pasta",
      "ingredients": {...},
      "ingredients_formatted": [
        "400 g spaghetti",
        "4 pieces eggs"
      ],
      "instructions": "1. Cook pasta...",
      "cuisine_type": "Italian",
      "taste_profile": "savory",
      "preparation_time": 10,
      "cooking_time": 15,
      "total_time": 25,
      "servings": 4,
      "difficulty": "easy",
      "is_favorite": false,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### Parse Text Recipe

**POST** `/api/recipes/parse-text/`

Parse recipe from unstructured text using AI.

**Request:**
```json
{
  "text": "Chocolate Chip Cookies\n\nIngredients:\n2 cups flour\n1 cup sugar\n...\n\nInstructions:\n1. Mix ingredients..."
}
```

**Response (201):**
```json
{
  "success": true,
  "message": "Recipe parsed and saved successfully",
  "data": {
    "id": "uuid",
    "title": "Chocolate Chip Cookies",
    "ingredients": [...],
    "source_type": "text",
    ...
  }
}
```

### Parse Image Recipe

**POST** `/api/recipes/parse-image/`

Extract recipe from image using OCR.

**Request (multipart/form-data):**
- `image`: Image file (JPEG, PNG, etc.)

**Response (201):**
```json
{
  "success": true,
  "message": "Recipe parsed from image successfully",
  "data": {
    "recipe": {...},
    "extracted_text": "The OCR-extracted text..."
  }
}
```

### Batch Import Recipes

**POST** `/api/recipes/batch-import/`

Import multiple recipes from a text file.

**Request (multipart/form-data):**
- `file`: Text file containing multiple recipes OR
- `text`: Raw text with multiple recipes

**Response (202):** (For large files - background processing)
```json
{
  "success": true,
  "message": "Batch import started in background",
  "data": {
    "task_id": "uuid"
  }
}
```

**Response (200):** (For small files - immediate)
```json
{
  "success": true,
  "message": "Successfully imported 5 recipes",
  "data": {
    "count": 5,
    "recipes": [...]
  }
}
```

### Search Recipes

**GET** `/api/recipes/search/`

Advanced recipe search.

**Query Parameters:**
- `query` (string): Search query
- `cuisine_type` (string): Filter by cuisine
- `difficulty` (string): Filter by difficulty
- `max_time` (integer): Max total time in minutes
- `taste_profile` (string): Filter by taste
- `has_all_ingredients` (boolean): Only recipes you can make now

**Example:**
```
GET /api/recipes/search/?query=pasta&cuisine_type=Italian&max_time=30
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "recipes": [...],
    "count": 10
  }
}
```

### Favorite Recipe

**POST** `/api/recipes/{id}/favorite/`

Add recipe to favorites.

**Response (201):**
```json
{
  "success": true,
  "message": "Recipe added to favorites",
  "data": {
    "id": "uuid",
    "recipe": {...},
    "created_at": "2024-01-15T12:00:00Z"
  }
}
```

### Unfavorite Recipe

**DELETE** `/api/recipes/{id}/unfavorite/`

Remove recipe from favorites.

## Shopping List

### Get Shopping List

**GET** `/api/shopping-list/`

Get user's shopping list.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "unpurchased": [
      {
        "id": "uuid",
        "ingredient_name": "Milk",
        "quantity": 2,
        "unit": "liters",
        "purchased": false,
        "notes": "",
        "recipe_id": null,
        "created_at": "2024-01-15T10:00:00Z"
      }
    ],
    "purchased": [],
    "total_count": 1,
    "unpurchased_count": 1,
    "purchased_count": 0
  }
}
```

### Add Item

**POST** `/api/shopping-list/add/`

Add item to shopping list.

**Request:**
```json
{
  "ingredient_name": "Milk",
  "quantity": 2,
  "unit": "liters",
  "notes": "2% fat"
}
```

### Toggle Purchased

**PATCH** `/api/shopping-list/{id}/toggle/`

Mark item as purchased/unpurchased.

### Add from Recipe

**POST** `/api/shopping-list/from-recipe/{recipe_id}/`

Add all recipe ingredients to shopping list.

**Response (200):**
```json
{
  "success": true,
  "message": "Added 6 items from recipe",
  "data": {
    "added_count": 6,
    "items": [...]
  }
}
```

### Add to Ingredients

**POST** `/api/shopping-list/add-to-ingredients/`

Transfer purchased items to ingredient inventory.

**Response (200):**
```json
{
  "success": true,
  "message": "Added 3 ingredients to inventory",
  "data": {
    "added_count": 3,
    "ingredients": [...]
  }
}
```

## Chatbot

### Send Message

**POST** `/api/chatbot/chat/`

Send message to AI chatbot.

**Request:**
```json
{
  "message": "What can I cook for dinner tonight?",
  "context": {}
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Response generated successfully",
  "data": {
    "response": "Based on your available ingredients, I recommend...",
    "recommended_recipes": [
      {
        "recipe": {...},
        "match_percentage": 85.5,
        "missing_ingredients": ["parsley"]
      }
    ],
    "chat_id": "uuid"
  }
}
```

### Get Chat History

**GET** `/api/chatbot/history/`

Get chat conversation history.

**Query Parameters:**
- `limit` (integer): Number of messages (default: 20)
- `offset` (integer): Pagination offset

**Response (200):**
```json
{
  "success": true,
  "data": {
    "chats": [
      {
        "id": "uuid",
        "message": "What can I cook?",
        "response": "Here are some suggestions...",
        "recommended_recipes_details": [...],
        "created_at": "2024-01-15T12:00:00Z"
      }
    ],
    "total_count": 10,
    "has_more": false
  }
}
```

### Get Recommendations

**POST** `/api/chatbot/recommend/`

Get recipe recommendations based on criteria.

**Request:**
```json
{
  "query": "Italian pasta",
  "cuisine_type": "Italian",
  "difficulty": "easy",
  "max_time": 30,
  "min_match_percentage": 70,
  "limit": 5
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "recommendations": [
      {
        "recipe": {...},
        "match_percentage": 85.0,
        "available_ingredients": ["pasta", "tomatoes", "garlic"],
        "missing_ingredients": ["basil"],
        "similarity_score": 0.92
      }
    ],
    "count": 5
  }
}
```

### Generate Meal Plan

**POST** `/api/chatbot/meal-plan/`

Generate a meal plan for multiple days.

**Request:**
```json
{
  "days": 7,
  "meals_per_day": 3
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "meal_plan": {
      "day_1": [
        {
          "meal_type": "breakfast",
          "recipe": {...},
          "match_percentage": 90,
          "missing_ingredients": []
        },
        {
          "meal_type": "lunch",
          "recipe": {...},
          "match_percentage": 75,
          "missing_ingredients": ["chicken"]
        }
      ]
    },
    "shopping_list": [
      {"ingredient": "chicken", "needed_for_meals": 3}
    ],
    "days": 7,
    "meals_per_day": 3
  }
}
```

## Storage

### Upload Recipe Image

**POST** `/api/storage/upload/recipe-image/`

Upload an image for a recipe.

**Request (multipart/form-data):**
- `image`: Image file

**Response (201):**
```json
{
  "success": true,
  "message": "Image uploaded successfully",
  "data": {
    "url": "https://your-project.supabase.co/storage/v1/object/public/recipe-images/..."
  }
}
```

## Error Responses

All endpoints return errors in this format:

**Response (4xx/5xx):**
```json
{
  "success": false,
  "message": "Error description",
  "errors": {
    "field_name": ["Error detail"]
  }
}
```

### Common Error Codes

- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found (resource doesn't exist)
- `429` - Too Many Requests (rate limit)
- `500` - Internal Server Error

## Rate Limits

- Authentication: 10 requests/minute
- General API: 60 requests/minute
- File uploads: 10 requests/minute

## Pagination

List endpoints support pagination:

**Query Parameters:**
- `page` (integer): Page number (default: 1)
- `page_size` (integer): Items per page (default: 20)

**Response includes:**
```json
{
  "results": [...],
  "count": 100,
  "next": true,
  "previous": false,
  "current_page": 1,
  "total_pages": 5
}
```

## Webhooks (Future)

Webhook support for:
- Recipe parsed
- Ingredient expiring
- Shopping list updated

## API Changelog

### v1.0.0 (2024-01-15)
- Initial release
- All core endpoints implemented

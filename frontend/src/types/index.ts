// Type definitions for Recipe Management System

export interface User {
  id: string
  email: string
  full_name?: string
  date_joined: string
}

export interface Ingredient {
  id: string
  name: string
  quantity?: number
  unit?: string
  category?: string
  expiry_date?: string
  notes?: string
  is_expiring_soon: boolean
  is_expired: boolean
  days_until_expiry?: number
  created_at: string
  updated_at: string
}

export interface RecipeIngredient {
  name: string
  quantity?: number
  unit?: string
  notes?: string
}

export interface Recipe {
  id: string
  title: string
  description?: string
  ingredients: any
  ingredients_formatted: string[]
  instructions: string
  cuisine_type?: string
  taste_profile?: string
  preparation_time?: number
  cooking_time?: number
  total_time: number
  servings?: number
  difficulty?: 'easy' | 'medium' | 'hard'
  image_url?: string
  source_type: 'text' | 'image' | 'manual'
  ingredient_names: string[]
  is_favorite: boolean
  created_at: string
  updated_at: string
}

export interface ShoppingListItem {
  id: string
  ingredient_name: string
  quantity?: number
  unit?: string
  purchased: boolean
  notes?: string
  recipe_id?: string
  created_at: string
  updated_at: string
}

export interface ChatMessage {
  id: string
  message: string
  response: string
  context?: any
  recommended_recipes?: string[]
  recommended_recipes_details?: Recipe[]
  created_at: string
}

export interface RecipeRecommendation {
  recipe: Recipe
  match_percentage: number
  available_ingredients: string[]
  missing_ingredients: string[]
  similarity_score?: number
}

export interface APIResponse<T> {
  success: boolean
  message: string
  data?: T
  errors?: any
}

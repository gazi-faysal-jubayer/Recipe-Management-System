-- ============================================
-- COMPLETE DATABASE MIGRATION
-- Run this entire file in Supabase SQL Editor
-- ============================================

-- ============================================
-- PART 1: Initial Schema
-- ============================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Ingredients table
CREATE TABLE IF NOT EXISTS ingredients (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
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
CREATE TABLE IF NOT EXISTS recipes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  title VARCHAR(500) NOT NULL,
  description TEXT,
  ingredients JSONB NOT NULL,
  instructions TEXT,
  cuisine_type VARCHAR(100),
  taste_profile VARCHAR(100),
  preparation_time INTEGER, -- in minutes
  cooking_time INTEGER, -- in minutes
  servings INTEGER,
  difficulty VARCHAR(50) CHECK (difficulty IN ('easy', 'medium', 'hard')),
  image_url TEXT,
  source_type VARCHAR(50) CHECK (source_type IN ('text', 'image', 'manual')),
  raw_text TEXT, -- Store original parsed text
  embedding vector(384), -- For sentence-transformers embeddings
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Shopping list table
CREATE TABLE IF NOT EXISTS shopping_list (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  ingredient_name VARCHAR(255) NOT NULL,
  quantity DECIMAL(10,2),
  unit VARCHAR(50),
  purchased BOOLEAN DEFAULT FALSE,
  notes TEXT,
  recipe_id UUID REFERENCES recipes(id) ON DELETE SET NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chat history table
CREATE TABLE IF NOT EXISTS chat_history (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  message TEXT NOT NULL,
  response TEXT NOT NULL,
  context JSONB, -- Store context like available ingredients, preferences
  recommended_recipes JSONB, -- Store IDs of recommended recipes
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Recipe favorites table
CREATE TABLE IF NOT EXISTS recipe_favorites (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  recipe_id UUID REFERENCES recipes(id) ON DELETE CASCADE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(user_id, recipe_id)
);

-- Ingredient categories lookup table
CREATE TABLE IF NOT EXISTS ingredient_categories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(100) NOT NULL UNIQUE,
  display_order INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Basic indexes for better performance
CREATE INDEX IF NOT EXISTS idx_ingredients_user_id ON ingredients(user_id);
CREATE INDEX IF NOT EXISTS idx_ingredients_category ON ingredients(category);
CREATE INDEX IF NOT EXISTS idx_ingredients_expiry ON ingredients(expiry_date);

CREATE INDEX IF NOT EXISTS idx_recipes_user_id ON recipes(user_id);
CREATE INDEX IF NOT EXISTS idx_recipes_cuisine ON recipes(cuisine_type);
CREATE INDEX IF NOT EXISTS idx_recipes_taste ON recipes(taste_profile);
CREATE INDEX IF NOT EXISTS idx_recipes_difficulty ON recipes(difficulty);

CREATE INDEX IF NOT EXISTS idx_shopping_list_user_id ON shopping_list(user_id);
CREATE INDEX IF NOT EXISTS idx_shopping_list_purchased ON shopping_list(purchased);

CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_created ON chat_history(created_at);

-- Vector index for similarity search (only if vector extension is available)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'vector') THEN
        CREATE INDEX IF NOT EXISTS idx_recipes_embedding ON recipes USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    END IF;
END $$;

-- Create update timestamp function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
DROP TRIGGER IF EXISTS update_ingredients_updated_at ON ingredients;
CREATE TRIGGER update_ingredients_updated_at BEFORE UPDATE ON ingredients
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_recipes_updated_at ON recipes;
CREATE TRIGGER update_recipes_updated_at BEFORE UPDATE ON recipes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_shopping_list_updated_at ON shopping_list;
CREATE TRIGGER update_shopping_list_updated_at BEFORE UPDATE ON shopping_list
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- PART 2: Row Level Security Policies
-- ============================================

-- Enable Row Level Security on all tables
ALTER TABLE ingredients ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipes ENABLE ROW LEVEL SECURITY;
ALTER TABLE shopping_list ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE recipe_favorites ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if any
DROP POLICY IF EXISTS "Users can view own ingredients" ON ingredients;
DROP POLICY IF EXISTS "Users can insert own ingredients" ON ingredients;
DROP POLICY IF EXISTS "Users can update own ingredients" ON ingredients;
DROP POLICY IF EXISTS "Users can delete own ingredients" ON ingredients;

DROP POLICY IF EXISTS "Users can view own recipes" ON recipes;
DROP POLICY IF EXISTS "Users can insert own recipes" ON recipes;
DROP POLICY IF EXISTS "Users can update own recipes" ON recipes;
DROP POLICY IF EXISTS "Users can delete own recipes" ON recipes;

DROP POLICY IF EXISTS "Users can view own shopping list" ON shopping_list;
DROP POLICY IF EXISTS "Users can insert own shopping list" ON shopping_list;
DROP POLICY IF EXISTS "Users can update own shopping list" ON shopping_list;
DROP POLICY IF EXISTS "Users can delete own shopping list" ON shopping_list;

DROP POLICY IF EXISTS "Users can view own chat history" ON chat_history;
DROP POLICY IF EXISTS "Users can insert own chat history" ON chat_history;

DROP POLICY IF EXISTS "Users can view own favorites" ON recipe_favorites;
DROP POLICY IF EXISTS "Users can insert own favorites" ON recipe_favorites;
DROP POLICY IF EXISTS "Users can delete own favorites" ON recipe_favorites;

-- Ingredients policies
CREATE POLICY "Users can view own ingredients" ON ingredients
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own ingredients" ON ingredients
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own ingredients" ON ingredients
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own ingredients" ON ingredients
    FOR DELETE USING (auth.uid() = user_id);

-- Recipes policies
CREATE POLICY "Users can view own recipes" ON recipes
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own recipes" ON recipes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own recipes" ON recipes
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own recipes" ON recipes
    FOR DELETE USING (auth.uid() = user_id);

-- Shopping list policies
CREATE POLICY "Users can view own shopping list" ON shopping_list
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own shopping list" ON shopping_list
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own shopping list" ON shopping_list
    FOR UPDATE USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own shopping list" ON shopping_list
    FOR DELETE USING (auth.uid() = user_id);

-- Chat history policies
CREATE POLICY "Users can view own chat history" ON chat_history
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own chat history" ON chat_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Recipe favorites policies
CREATE POLICY "Users can view own favorites" ON recipe_favorites
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own favorites" ON recipe_favorites
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own favorites" ON recipe_favorites
    FOR DELETE USING (auth.uid() = user_id);

-- Ingredient categories policies (public read)
CREATE POLICY "Anyone can view ingredient categories" ON ingredient_categories
    FOR SELECT USING (true);

-- Service role policies for admin operations
DROP POLICY IF EXISTS "Service role full access to ingredients" ON ingredients;
CREATE POLICY "Service role full access to ingredients" ON ingredients
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

DROP POLICY IF EXISTS "Service role full access to recipes" ON recipes;
CREATE POLICY "Service role full access to recipes" ON recipes
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

DROP POLICY IF EXISTS "Service role full access to shopping_list" ON shopping_list;
CREATE POLICY "Service role full access to shopping_list" ON shopping_list
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

DROP POLICY IF EXISTS "Service role full access to chat_history" ON chat_history;
CREATE POLICY "Service role full access to chat_history" ON chat_history
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

DROP POLICY IF EXISTS "Service role full access to recipe_favorites" ON recipe_favorites;
CREATE POLICY "Service role full access to recipe_favorites" ON recipe_favorites
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

DROP POLICY IF EXISTS "Service role can manage ingredient_categories" ON ingredient_categories;
CREATE POLICY "Service role can manage ingredient_categories" ON ingredient_categories
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

-- ============================================
-- PART 3: Additional Indexes and Functions
-- ============================================

-- Full text search indexes for recipes
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_attribute WHERE attrelid = 'recipes'::regclass AND attname = 'search_vector') THEN
        ALTER TABLE recipes ADD COLUMN search_vector tsvector 
            GENERATED ALWAYS AS (
                setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
                setweight(to_tsvector('english', coalesce(description, '')), 'B') ||
                setweight(to_tsvector('english', coalesce(cuisine_type, '')), 'C')
            ) STORED;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_recipes_search ON recipes USING GIN(search_vector);

-- Full text search indexes for ingredients
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_attribute WHERE attrelid = 'ingredients'::regclass AND attname = 'search_vector') THEN
        ALTER TABLE ingredients ADD COLUMN search_vector tsvector 
            GENERATED ALWAYS AS (
                to_tsvector('english', coalesce(name, ''))
            ) STORED;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_ingredients_search ON ingredients USING GIN(search_vector);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_recipes_user_cuisine ON recipes(user_id, cuisine_type);
CREATE INDEX IF NOT EXISTS idx_recipes_user_difficulty ON recipes(user_id, difficulty);
CREATE INDEX IF NOT EXISTS idx_recipes_user_created ON recipes(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_ingredients_user_category ON ingredients(user_id, category);
CREATE INDEX IF NOT EXISTS idx_ingredients_user_expiry ON ingredients(user_id, expiry_date);
CREATE INDEX IF NOT EXISTS idx_ingredients_user_name ON ingredients(user_id, name);

CREATE INDEX IF NOT EXISTS idx_shopping_list_user_purchased ON shopping_list(user_id, purchased);
CREATE INDEX IF NOT EXISTS idx_shopping_list_user_created ON shopping_list(user_id, created_at DESC);

-- Index for recipe ingredients JSONB
CREATE INDEX IF NOT EXISTS idx_recipes_ingredients ON recipes USING GIN(ingredients);

-- Index for chat history context JSONB
CREATE INDEX IF NOT EXISTS idx_chat_history_context ON chat_history USING GIN(context);
CREATE INDEX IF NOT EXISTS idx_chat_history_recommendations ON chat_history USING GIN(recommended_recipes);

-- Index for faster recipe favorites lookups
CREATE INDEX IF NOT EXISTS idx_recipe_favorites_recipe ON recipe_favorites(recipe_id);

-- Function to search recipes by ingredients
CREATE OR REPLACE FUNCTION search_recipes_by_ingredients(
    user_uuid UUID,
    ingredient_names TEXT[]
)
RETURNS TABLE (
    recipe_id UUID,
    title VARCHAR,
    matched_ingredients INTEGER,
    total_ingredients INTEGER,
    match_percentage NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    WITH recipe_ingredients AS (
        SELECT 
            r.id,
            r.title,
            jsonb_array_elements_text(r.ingredients->'items') as ingredient_name
        FROM recipes r
        WHERE r.user_id = user_uuid
    ),
    matched AS (
        SELECT 
            ri.id,
            ri.title,
            COUNT(CASE WHEN LOWER(ri.ingredient_name) = ANY(
                SELECT LOWER(unnest(ingredient_names))
            ) THEN 1 END) as matched_count,
            COUNT(*) as total_count
        FROM recipe_ingredients ri
        GROUP BY ri.id, ri.title
    )
    SELECT 
        m.id,
        m.title,
        m.matched_count::INTEGER,
        m.total_count::INTEGER,
        ROUND((m.matched_count::NUMERIC / m.total_count::NUMERIC) * 100, 2) as match_percentage
    FROM matched m
    WHERE m.matched_count > 0
    ORDER BY match_percentage DESC, m.title;
END;
$$ LANGUAGE plpgsql;

-- Function to get expiring ingredients
CREATE OR REPLACE FUNCTION get_expiring_ingredients(
    user_uuid UUID,
    days_ahead INTEGER DEFAULT 7
)
RETURNS TABLE (
    id UUID,
    name VARCHAR,
    quantity DECIMAL,
    unit VARCHAR,
    expiry_date DATE,
    days_until_expiry INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        i.id,
        i.name,
        i.quantity,
        i.unit,
        i.expiry_date,
        (i.expiry_date - CURRENT_DATE)::INTEGER as days_until_expiry
    FROM ingredients i
    WHERE i.user_id = user_uuid
        AND i.expiry_date IS NOT NULL
        AND i.expiry_date <= CURRENT_DATE + days_ahead
        AND i.expiry_date >= CURRENT_DATE
    ORDER BY i.expiry_date;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- MIGRATION COMPLETE!
-- ============================================

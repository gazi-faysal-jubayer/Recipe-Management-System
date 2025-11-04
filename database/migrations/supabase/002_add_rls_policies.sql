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
CREATE POLICY "Service role full access to ingredients" ON ingredients
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role full access to recipes" ON recipes
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role full access to shopping_list" ON shopping_list
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role full access to chat_history" ON chat_history
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role full access to recipe_favorites" ON recipe_favorites
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

CREATE POLICY "Service role can manage ingredient_categories" ON ingredient_categories
    FOR ALL USING (auth.jwt()->>'role' = 'service_role');

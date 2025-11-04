-- Additional performance indexes

-- Full text search indexes for recipes
ALTER TABLE recipes ADD COLUMN search_vector tsvector 
    GENERATED ALWAYS AS (
        setweight(to_tsvector('english', coalesce(title, '')), 'A') ||
        setweight(to_tsvector('english', coalesce(description, '')), 'B') ||
        setweight(to_tsvector('english', coalesce(cuisine_type, '')), 'C')
    ) STORED;

CREATE INDEX idx_recipes_search ON recipes USING GIN(search_vector);

-- Full text search indexes for ingredients
ALTER TABLE ingredients ADD COLUMN search_vector tsvector 
    GENERATED ALWAYS AS (
        to_tsvector('english', coalesce(name, ''))
    ) STORED;

CREATE INDEX idx_ingredients_search ON ingredients USING GIN(search_vector);

-- Composite indexes for common queries
CREATE INDEX idx_recipes_user_cuisine ON recipes(user_id, cuisine_type);
CREATE INDEX idx_recipes_user_difficulty ON recipes(user_id, difficulty);
CREATE INDEX idx_recipes_user_created ON recipes(user_id, created_at DESC);

CREATE INDEX idx_ingredients_user_category ON ingredients(user_id, category);
CREATE INDEX idx_ingredients_user_expiry ON ingredients(user_id, expiry_date);
CREATE INDEX idx_ingredients_user_name ON ingredients(user_id, name);

CREATE INDEX idx_shopping_list_user_purchased ON shopping_list(user_id, purchased);
CREATE INDEX idx_shopping_list_user_created ON shopping_list(user_id, created_at DESC);

-- Index for recipe ingredients JSONB
CREATE INDEX idx_recipes_ingredients ON recipes USING GIN(ingredients);

-- Index for chat history context JSONB
CREATE INDEX idx_chat_history_context ON chat_history USING GIN(context);
CREATE INDEX idx_chat_history_recommendations ON chat_history USING GIN(recommended_recipes);

-- Index for faster recipe favorites lookups
CREATE INDEX idx_recipe_favorites_recipe ON recipe_favorites(recipe_id);

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

"""
Generate embeddings for recipes
"""
from sentence_transformers import SentenceTransformer
import numpy as np
import psycopg2
from psycopg2.extras import execute_values
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')


def generate_embedding(text: str) -> np.ndarray:
    """Generate embedding vector for text"""
    return model.encode(text)


def update_recipe_embeddings():
    """Update embeddings for all recipes without embeddings"""
    
    # Connect to database
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cursor = conn.cursor()
    
    try:
        # Get recipes without embeddings
        cursor.execute("""
            SELECT id, title, description, ingredients
            FROM recipes
            WHERE embedding IS NULL
        """)
        
        recipes = cursor.fetchall()
        print(f"Found {len(recipes)} recipes without embeddings")
        
        # Generate and update embeddings
        for recipe_id, title, description, ingredients in recipes:
            # Combine text for embedding
            ingredient_names = []
            if isinstance(ingredients, dict) and 'items' in ingredients:
                ingredient_names = [ing.get('name', '') for ing in ingredients['items']]
            
            embedding_text = f"{title} {description or ''} {' '.join(ingredient_names)}"
            
            # Generate embedding
            embedding = generate_embedding(embedding_text)
            
            # Update database
            cursor.execute("""
                UPDATE recipes
                SET embedding = %s
                WHERE id = %s
            """, (embedding.tolist(), recipe_id))
            
            print(f"Updated embedding for: {title}")
        
        conn.commit()
        print(f"✓ Successfully updated {len(recipes)} recipe embeddings")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()


def batch_generate_embeddings(texts: list) -> np.ndarray:
    """Generate embeddings for multiple texts at once"""
    return model.encode(texts)


if __name__ == "__main__":
    print("Starting embedding generation...")
    update_recipe_embeddings()

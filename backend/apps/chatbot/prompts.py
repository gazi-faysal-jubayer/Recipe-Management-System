"""
Prompts for chatbot interactions
"""

RECIPE_ASSISTANT_SYSTEM_PROMPT = """You are Mofa's Recipe Assistant, a helpful AI chef that helps users discover and cook delicious recipes based on their available ingredients and preferences.

Your primary responsibilities:
1. Recommend recipes based on available ingredients and user preferences
2. Suggest recipes for specific occasions, moods, or cravings
3. Help users understand what they can cook with their current ingredients
4. Provide cooking tips and substitution suggestions
5. Help users plan meals and manage their ingredients

When recommending recipes:
- Consider the user's available ingredients (they will be provided in context)
- Match recipes to their stated preferences (sweet, savory, spicy, etc.)
- Mention the percentage of ingredients they have available
- List any missing ingredients they would need
- Be encouraging about what they can make

Keep responses friendly, concise, and focused on helping the user cook something delicious.

If the user asks about non-cooking topics, politely redirect the conversation back to recipes and cooking."""

RECIPE_RECOMMENDATION_PROMPT = """Based on the user's request and their available ingredients, recommend suitable recipes.

User Request: {user_message}

Available Ingredients:
{available_ingredients}

User Preferences:
- Cuisine preferences: {cuisine_preferences}
- Dietary restrictions: {dietary_restrictions}
- Time constraints: {time_constraints}

Found Recipes:
{recipe_matches}

Please provide a helpful response that:
1. Acknowledges the user's request
2. Recommends the best matching recipes
3. Mentions the ingredient match percentage
4. Lists missing ingredients if any
5. Provides brief cooking tips or substitution suggestions
6. Encourages the user to try the recipes

Keep the response conversational and helpful."""

INGREDIENT_ANALYSIS_PROMPT = """Analyze what recipes can be made with these ingredients:

Available Ingredients:
{ingredients_list}

Consider:
1. Complete recipes (100% ingredients available)
2. Nearly complete recipes (80%+ ingredients available)
3. Possible recipes with substitutions
4. Shopping suggestions for missing ingredients

Provide practical cooking suggestions."""

MEAL_PLANNING_PROMPT = """Help the user plan their meals based on their preferences and available ingredients.

User Request: {user_message}
Days to Plan: {days}
Meals per Day: {meals_per_day}
Available Ingredients: {available_ingredients}

Suggested Meal Plan:
{meal_plan}

Provide a helpful response that:
1. Presents the meal plan in an organized way
2. Highlights which meals can be made with current ingredients
3. Suggests a shopping list for missing ingredients
4. Offers meal prep tips
5. Provides alternatives or substitutions

Keep the response practical and encouraging."""

COOKING_HELP_PROMPT = """Provide cooking assistance for the following query:

User Question: {user_message}
Recipe Context: {recipe_context}

Provide helpful cooking advice that:
1. Directly answers the user's question
2. Offers practical tips
3. Suggests alternatives if applicable
4. Keeps safety in mind
5. Encourages confidence in cooking

Be specific and actionable in your response."""

def format_recipe_matches(recipe_matches):
    """Format recipe matches for inclusion in prompts"""
    if not recipe_matches:
        return "No recipes found matching your criteria."
    
    formatted = []
    for match in recipe_matches:
        recipe = match['recipe']
        formatted_recipe = f"""
Recipe: {recipe.title}
- Match: {match['match_percentage']:.0f}% of ingredients available
- Cuisine: {recipe.cuisine_type or 'Various'}
- Difficulty: {recipe.difficulty or 'Medium'}
- Time: {recipe.total_time or 'Not specified'} minutes
- Missing ingredients: {', '.join(match['missing_ingredients']) if match['missing_ingredients'] else 'None - you have everything!'}
- Description: {recipe.description or 'A delicious recipe'}
"""
        formatted.append(formatted_recipe.strip())
    
    return "\n\n".join(formatted)


def format_ingredients_list(ingredients):
    """Format ingredients list for prompts"""
    if not ingredients:
        return "No ingredients currently in inventory."
    
    formatted = []
    for ingredient in ingredients:
        if ingredient.quantity and ingredient.unit:
            formatted.append(f"- {ingredient.name} ({ingredient.quantity} {ingredient.unit})")
        else:
            formatted.append(f"- {ingredient.name}")
    
    return "\n".join(formatted)


def format_meal_plan(meal_plan):
    """Format meal plan for prompts"""
    if not meal_plan:
        return "No meal plan generated."
    
    formatted = []
    for day, meals in meal_plan.items():
        day_num = day.replace('day_', 'Day ')
        formatted.append(f"\n{day_num}:")
        
        for meal in meals:
            recipe = meal['recipe']
            formatted.append(f"  {meal['meal_type'].title()}: {recipe.title}")
            if meal['missing_ingredients']:
                formatted.append(f"    Missing: {', '.join(meal['missing_ingredients'])}")
    
    return "\n".join(formatted)

'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Heart, Trash2, Clock, Users, ChefHat } from 'lucide-react'
import { api } from '@/lib/api/client'
import { toast } from 'react-hot-toast'
import { useState } from 'react'

interface RecipeGridProps {
  recipes: any[]
  onDelete: (id: string) => void
  onRefresh: () => void
}

export function RecipeGrid({ recipes, onDelete, onRefresh }: RecipeGridProps) {
  const [favoriting, setFavoriting] = useState<string | null>(null)

  const toggleFavorite = async (recipe: any) => {
    setFavoriting(recipe.id)
    try {
      if (recipe.is_favorite) {
        await api.recipes.unfavorite(recipe.id)
        toast.success('Removed from favorites')
      } else {
        await api.recipes.favorite(recipe.id)
        toast.success('Added to favorites')
      }
      onRefresh()
    } catch (error) {
      toast.error('Failed to update favorite')
    } finally {
      setFavoriting(null)
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {recipes.map((recipe) => (
        <Card key={recipe.id} className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <CardTitle className="text-lg line-clamp-2">{recipe.title}</CardTitle>
                {recipe.cuisine_type && (
                  <Badge variant="secondary" className="mt-2">
                    {recipe.cuisine_type}
                  </Badge>
                )}
              </div>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => toggleFavorite(recipe)}
                disabled={favoriting === recipe.id}
              >
                <Heart
                  className={`h-5 w-5 ${
                    recipe.is_favorite ? 'fill-red-500 text-red-500' : 'text-gray-400'
                  }`}
                />
              </Button>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            {recipe.description && (
              <p className="text-sm text-gray-600 line-clamp-2">{recipe.description}</p>
            )}
            
            <div className="flex flex-wrap gap-2 text-sm text-gray-600">
              {recipe.total_time && (
                <div className="flex items-center gap-1">
                  <Clock className="h-4 w-4" />
                  <span>{recipe.total_time} min</span>
                </div>
              )}
              {recipe.servings && (
                <div className="flex items-center gap-1">
                  <Users className="h-4 w-4" />
                  <span>{recipe.servings} servings</span>
                </div>
              )}
              {recipe.difficulty && (
                <div className="flex items-center gap-1">
                  <ChefHat className="h-4 w-4" />
                  <span className="capitalize">{recipe.difficulty}</span>
                </div>
              )}
            </div>

            {recipe.taste_profile && (
              <Badge className="bg-purple-100 text-purple-800">
                {recipe.taste_profile}
              </Badge>
            )}

            <div className="flex gap-2 pt-2">
              <Button variant="outline" className="flex-1" size="sm">
                View Details
              </Button>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => onDelete(recipe.id)}
              >
                <Trash2 className="h-4 w-4 text-red-500" />
              </Button>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  )
}

'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { api } from '@/lib/api/client'
import { toast } from 'react-hot-toast'
import { Loader2 } from 'lucide-react'

interface AddRecipeDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
}

export function AddRecipeDialog({ open, onOpenChange, onSuccess }: AddRecipeDialogProps) {
  const [loading, setLoading] = useState(false)
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    instructions: '',
    cuisine_type: '',
    preparation_time: '',
    cooking_time: '',
    servings: '',
    difficulty: 'medium',
    ingredients: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Parse ingredients from textarea
      const ingredientsArray = formData.ingredients
        .split('\n')
        .filter(line => line.trim())
        .map(line => ({ name: line.trim() }))

      const data = {
        ...formData,
        ingredients: ingredientsArray,
        preparation_time: formData.preparation_time ? parseInt(formData.preparation_time) : null,
        cooking_time: formData.cooking_time ? parseInt(formData.cooking_time) : null,
        servings: formData.servings ? parseInt(formData.servings) : null,
      }

      await api.recipes.create(data)
      toast.success('Recipe added successfully')
      onSuccess()
      onOpenChange(false)
      setFormData({
        title: '',
        description: '',
        instructions: '',
        cuisine_type: '',
        preparation_time: '',
        cooking_time: '',
        servings: '',
        difficulty: 'medium',
        ingredients: '',
      })
    } catch (error) {
      toast.error('Failed to add recipe')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Add Recipe</DialogTitle>
          <DialogDescription>
            Create a new recipe manually
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="space-y-4 py-4">
            <div className="space-y-2">
              <Label htmlFor="title">Title *</Label>
              <Input
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                required
                disabled={loading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                disabled={loading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="ingredients">Ingredients (one per line) *</Label>
              <Textarea
                id="ingredients"
                value={formData.ingredients}
                onChange={(e) => setFormData({ ...formData, ingredients: e.target.value })}
                placeholder="2 cups flour&#10;1 cup sugar&#10;3 eggs"
                rows={5}
                required
                disabled={loading}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="instructions">Instructions *</Label>
              <Textarea
                id="instructions"
                value={formData.instructions}
                onChange={(e) => setFormData({ ...formData, instructions: e.target.value })}
                rows={5}
                required
                disabled={loading}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="cuisine_type">Cuisine Type</Label>
                <Input
                  id="cuisine_type"
                  value={formData.cuisine_type}
                  onChange={(e) => setFormData({ ...formData, cuisine_type: e.target.value })}
                  disabled={loading}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="difficulty">Difficulty</Label>
                <select
                  id="difficulty"
                  value={formData.difficulty}
                  onChange={(e) => setFormData({ ...formData, difficulty: e.target.value })}
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                  disabled={loading}
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="preparation_time">Prep Time (min)</Label>
                <Input
                  id="preparation_time"
                  type="number"
                  value={formData.preparation_time}
                  onChange={(e) => setFormData({ ...formData, preparation_time: e.target.value })}
                  disabled={loading}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="cooking_time">Cook Time (min)</Label>
                <Input
                  id="cooking_time"
                  type="number"
                  value={formData.cooking_time}
                  onChange={(e) => setFormData({ ...formData, cooking_time: e.target.value })}
                  disabled={loading}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="servings">Servings</Label>
                <Input
                  id="servings"
                  type="number"
                  value={formData.servings}
                  onChange={(e) => setFormData({ ...formData, servings: e.target.value })}
                  disabled={loading}
                />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" onClick={() => onOpenChange(false)} disabled={loading}>
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Add Recipe
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}

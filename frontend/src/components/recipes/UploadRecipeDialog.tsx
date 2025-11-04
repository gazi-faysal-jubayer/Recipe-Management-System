'use client'

import { useState } from 'react'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { api } from '@/lib/api/client'
import { toast } from 'react-hot-toast'
import { Loader2, FileText, Image as ImageIcon } from 'lucide-react'

interface UploadRecipeDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onSuccess: () => void
}

export function UploadRecipeDialog({ open, onOpenChange, onSuccess }: UploadRecipeDialogProps) {
  const [loading, setLoading] = useState(false)
  const [recipeText, setRecipeText] = useState('')
  const [selectedImage, setSelectedImage] = useState<File | null>(null)

  const handleTextUpload = async () => {
    if (!recipeText.trim()) {
      toast.error('Please enter recipe text')
      return
    }

    setLoading(true)
    try {
      await api.recipes.parseText({ text: recipeText })
      toast.success('Recipe parsed and saved successfully!')
      onSuccess()
      onOpenChange(false)
      setRecipeText('')
    } catch (error) {
      toast.error('Failed to parse recipe')
    } finally {
      setLoading(false)
    }
  }

  const handleImageUpload = async () => {
    if (!selectedImage) {
      toast.error('Please select an image')
      return
    }

    setLoading(true)
    try {
      await api.recipes.parseImage(selectedImage)
      toast.success('Recipe extracted from image successfully!')
      onSuccess()
      onOpenChange(false)
      setSelectedImage(null)
    } catch (error) {
      toast.error('Failed to extract recipe from image')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px]">
        <DialogHeader>
          <DialogTitle>Upload Recipe</DialogTitle>
          <DialogDescription>
            Parse a recipe from text or image using AI
          </DialogDescription>
        </DialogHeader>
        
        <Tabs defaultValue="text" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="text">
              <FileText className="mr-2 h-4 w-4" />
              Text
            </TabsTrigger>
            <TabsTrigger value="image">
              <ImageIcon className="mr-2 h-4 w-4" />
              Image
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="text" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="recipe-text">Recipe Text</Label>
              <Textarea
                id="recipe-text"
                placeholder="Paste your recipe here...&#10;&#10;Example:&#10;Chocolate Chip Cookies&#10;&#10;Ingredients:&#10;2 cups flour&#10;1 cup sugar&#10;...&#10;&#10;Instructions:&#10;1. Mix flour and sugar&#10;2. ..."
                value={recipeText}
                onChange={(e) => setRecipeText(e.target.value)}
                rows={12}
                disabled={loading}
              />
            </div>
            <DialogFooter>
              <Button onClick={handleTextUpload} disabled={loading}>
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Parse Recipe
              </Button>
            </DialogFooter>
          </TabsContent>
          
          <TabsContent value="image" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="recipe-image">Recipe Image</Label>
              <div className="border-2 border-dashed rounded-lg p-8 text-center">
                {selectedImage ? (
                  <div className="space-y-2">
                    <p className="text-sm text-gray-600">{selectedImage.name}</p>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSelectedImage(null)}
                      disabled={loading}
                    >
                      Change Image
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <ImageIcon className="mx-auto h-12 w-12 text-gray-400" />
                    <p className="text-sm text-gray-600">
                      Click to upload or drag and drop
                    </p>
                    <input
                      id="recipe-image"
                      type="file"
                      accept="image/*"
                      className="hidden"
                      onChange={(e) => {
                        const file = e.target.files?.[0]
                        if (file) setSelectedImage(file)
                      }}
                      disabled={loading}
                    />
                    <Button
                      variant="outline"
                      onClick={() => document.getElementById('recipe-image')?.click()}
                      disabled={loading}
                    >
                      Select Image
                    </Button>
                  </div>
                )}
              </div>
            </div>
            <DialogFooter>
              <Button onClick={handleImageUpload} disabled={loading || !selectedImage}>
                {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Extract Recipe
              </Button>
            </DialogFooter>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  )
}

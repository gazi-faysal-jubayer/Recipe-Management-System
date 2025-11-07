'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Plus, Search, Filter, Download, Upload } from 'lucide-react'
import { api } from '@/lib/api/client'
import { toast } from 'react-hot-toast'
import { IngredientTable } from '@/components/ingredients/IngredientTable'
import { AddIngredientDialog } from '@/components/ingredients/AddIngredientDialog'
import { EditIngredientDialog } from '@/components/ingredients/EditIngredientDialog'

export default function IngredientsPage() {
  const [ingredients, setIngredients] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterCategory, setFilterCategory] = useState('')
  const [showExpiring, setShowExpiring] = useState(false)
  const [addDialogOpen, setAddDialogOpen] = useState(false)
  const [editingIngredient, setEditingIngredient] = useState(null)

  useEffect(() => {
    fetchIngredients()
  }, [filterCategory, showExpiring])

  const fetchIngredients = async () => {
    try {
      setLoading(true)
      const params: any = {}
      if (filterCategory) params.category = filterCategory
      if (showExpiring) params.expiring = true
      if (searchTerm) params.search = searchTerm

      const response = await api.ingredients.list(params)
      setIngredients(response.data.results || response.data)
    } catch (error) {
      toast.error('Failed to fetch ingredients')
      console.error(error); 
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = () => {
    fetchIngredients()
  }

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this ingredient?')) return

    try {
      await api.ingredients.delete(id)
      toast.success('Ingredient deleted')
      fetchIngredients()
    } catch (error) {
      toast.error('Failed to delete ingredient')
    }
  }

  const handleEdit = (ingredient: any) => {
    setEditingIngredient(ingredient)
  }

  const handleImportCSV = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    try {
      await api.ingredients.importCSV(file)
      toast.success('Ingredients imported successfully')
      fetchIngredients()
    } catch (error) {
      toast.error('Failed to import CSV')
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Ingredients</h1>
          <p className="text-gray-600 mt-1">Manage your kitchen inventory</p>
        </div>
        <div className="flex gap-2">
          <label htmlFor="csv-upload">
            <Button variant="outline" asChild>
              <span className="cursor-pointer">
                <Upload className="mr-2 h-4 w-4" />
                Import CSV
              </span>
            </Button>
          </label>
          <input
            id="csv-upload"
            type="file"
            accept=".csv"
            className="hidden"
            onChange={handleImportCSV}
          />
          <Button onClick={() => setAddDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Add Ingredient
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total Ingredients
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{ingredients.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Expiring Soon
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">
              {ingredients.filter((i: any) => i.is_expiring_soon).length}
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Expired
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {ingredients.filter((i: any) => i.is_expired).length}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1 flex gap-2">
              <Input
                placeholder="Search ingredients..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              />
              <Button onClick={handleSearch}>
                <Search className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex gap-2">
              <Button
                variant={showExpiring ? 'default' : 'outline'}
                onClick={() => setShowExpiring(!showExpiring)}
              >
                <Filter className="mr-2 h-4 w-4" />
                Expiring Soon
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Ingredients Table */}
      <Card>
        <CardContent className="pt-6">
          {loading ? (
            <div className="text-center py-8">Loading...</div>
          ) : ingredients.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              No ingredients found. Add your first ingredient to get started!
            </div>
          ) : (
            <IngredientTable
              ingredients={ingredients}
              onEdit={handleEdit}
              onDelete={handleDelete}
            />
          )}
        </CardContent>
      </Card>

      {/* Dialogs */}
      <AddIngredientDialog
        open={addDialogOpen}
        onOpenChange={setAddDialogOpen}
        onSuccess={fetchIngredients}
      />
      {editingIngredient && (
        <EditIngredientDialog
          ingredient={editingIngredient}
          open={!!editingIngredient}
          onOpenChange={(open) => !open && setEditingIngredient(null)}
          onSuccess={fetchIngredients}
        />
      )}
    </div>
  )
}

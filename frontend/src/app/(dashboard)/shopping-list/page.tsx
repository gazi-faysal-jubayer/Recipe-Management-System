'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Plus, Trash2, Check, ShoppingCart, Package } from 'lucide-react'
import { api } from '@/lib/api/client'
import { toast } from 'react-hot-toast'
import { AddShoppingItemDialog } from '@/components/shopping/AddShoppingItemDialog'

export default function ShoppingListPage() {
  const [items, setItems] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [addDialogOpen, setAddDialogOpen] = useState(false)

  useEffect(() => {
    fetchItems()
  }, [])

  const fetchItems = async () => {
    try {
      setLoading(true)
      const response = await api.shoppingList.list()
      const data = response.data.data || response.data
      setItems([
        ...(data.unpurchased || []),
        ...(data.purchased || [])
      ])
    } catch (error) {
      toast.error('Failed to fetch shopping list')
    } finally {
      setLoading(false)
    }
  }

  const handleToggle = async (id: string) => {
    try {
      await api.shoppingList.toggle(id)
      fetchItems()
    } catch (error) {
      toast.error('Failed to update item')
    }
  }

  const handleDelete = async (id: string) => {
    try {
      await api.shoppingList.delete(id)
      toast.success('Item deleted')
      fetchItems()
    } catch (error) {
      toast.error('Failed to delete item')
    }
  }

  const handleClearPurchased = async () => {
    if (!confirm('Remove all purchased items from the list?')) return

    try {
      await api.shoppingList.clearPurchased()
      toast.success('Purchased items cleared')
      fetchItems()
    } catch (error) {
      toast.error('Failed to clear purchased items')
    }
  }

  const handleAddToIngredients = async () => {
    if (!confirm('Add all purchased items to your ingredients inventory?')) return

    try {
      await api.shoppingList.addToIngredients()
      toast.success('Items added to inventory')
      fetchItems()
    } catch (error) {
      toast.error('Failed to add to inventory')
    }
  }

  const unpurchased = items.filter(item => !item.purchased)
  const purchased = items.filter(item => item.purchased)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Shopping List</h1>
          <p className="text-gray-600 mt-1">Manage your shopping needs</p>
        </div>
        <div className="flex gap-2">
          {purchased.length > 0 && (
            <>
              <Button variant="outline" onClick={handleAddToIngredients}>
                <Package className="mr-2 h-4 w-4" />
                Add to Inventory
              </Button>
              <Button variant="outline" onClick={handleClearPurchased}>
                <Trash2 className="mr-2 h-4 w-4" />
                Clear Purchased
              </Button>
            </>
          )}
          <Button onClick={() => setAddDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            Add Item
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Total Items
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{items.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              To Buy
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">{unpurchased.length}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-gray-600">
              Purchased
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{purchased.length}</div>
          </CardContent>
        </Card>
      </div>

      {/* Shopping List */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Unpurchased */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <ShoppingCart className="h-5 w-5" />
              To Buy ({unpurchased.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p className="text-center py-4">Loading...</p>
            ) : unpurchased.length === 0 ? (
              <p className="text-center py-8 text-gray-500">No items to buy</p>
            ) : (
              <div className="space-y-2">
                {unpurchased.map((item) => (
                  <div key={item.id} className="flex items-center gap-2 p-3 rounded-lg border hover:bg-gray-50">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleToggle(item.id)}
                      className="p-1 h-8 w-8"
                    >
                      <div className="h-5 w-5 rounded border-2 border-gray-300" />
                    </Button>
                    <div className="flex-1">
                      <p className="font-medium">{item.ingredient_name}</p>
                      {(item.quantity || item.unit) && (
                        <p className="text-sm text-gray-600">
                          {item.quantity} {item.unit}
                        </p>
                      )}
                    </div>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDelete(item.id)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Purchased */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Check className="h-5 w-5" />
              Purchased ({purchased.length})
            </CardTitle>
          </CardHeader>
          <CardContent>
            {purchased.length === 0 ? (
              <p className="text-center py-8 text-gray-500">No purchased items</p>
            ) : (
              <div className="space-y-2">
                {purchased.map((item) => (
                  <div key={item.id} className="flex items-center gap-2 p-3 rounded-lg border bg-green-50">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleToggle(item.id)}
                      className="p-1 h-8 w-8"
                    >
                      <div className="h-5 w-5 rounded bg-green-500 flex items-center justify-center">
                        <Check className="h-4 w-4 text-white" />
                      </div>
                    </Button>
                    <div className="flex-1">
                      <p className="font-medium line-through text-gray-600">{item.ingredient_name}</p>
                      {(item.quantity || item.unit) && (
                        <p className="text-sm text-gray-500">
                          {item.quantity} {item.unit}
                        </p>
                      )}
                    </div>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDelete(item.id)}
                    >
                      <Trash2 className="h-4 w-4 text-red-500" />
                    </Button>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      <AddShoppingItemDialog
        open={addDialogOpen}
        onOpenChange={setAddDialogOpen}
        onSuccess={fetchItems}
      />
    </div>
  )
}

'use client'

import { Button } from '@/components/ui/button'
import { Edit, Trash2, AlertCircle } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { format } from 'date-fns'

interface IngredientTableProps {
  ingredients: any[]
  onEdit: (ingredient: any) => void
  onDelete: (id: string) => void
}

export function IngredientTable({ ingredients, onEdit, onDelete }: IngredientTableProps) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b">
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Name</th>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Quantity</th>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Category</th>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Expiry Date</th>
            <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Status</th>
            <th className="px-4 py-3 text-right text-sm font-medium text-gray-600">Actions</th>
          </tr>
        </thead>
        <tbody>
          {ingredients.map((ingredient) => (
            <tr key={ingredient.id} className="border-b hover:bg-gray-50">
              <td className="px-4 py-3 text-sm font-medium">{ingredient.name}</td>
              <td className="px-4 py-3 text-sm">
                {ingredient.quantity && ingredient.unit
                  ? `${ingredient.quantity} ${ingredient.unit}`
                  : '-'}
              </td>
              <td className="px-4 py-3 text-sm">
                {ingredient.category ? (
                  <Badge variant="secondary">{ingredient.category}</Badge>
                ) : (
                  '-'
                )}
              </td>
              <td className="px-4 py-3 text-sm">
                {ingredient.expiry_date ? (
                  <div className="flex items-center gap-2">
                    {format(new Date(ingredient.expiry_date), 'MMM dd, yyyy')}
                    {ingredient.is_expiring_soon && (
                      <AlertCircle className="h-4 w-4 text-orange-500" />
                    )}
                  </div>
                ) : (
                  '-'
                )}
              </td>
              <td className="px-4 py-3 text-sm">
                {ingredient.is_expired ? (
                  <Badge variant="destructive">Expired</Badge>
                ) : ingredient.is_expiring_soon ? (
                  <Badge className="bg-orange-500">Expiring Soon</Badge>
                ) : (
                  <Badge className="bg-green-500">Fresh</Badge>
                )}
              </td>
              <td className="px-4 py-3 text-right">
                <div className="flex justify-end gap-2">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => onEdit(ingredient)}
                  >
                    <Edit className="h-4 w-4" />
                  </Button>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => onDelete(ingredient.id)}
                  >
                    <Trash2 className="h-4 w-4 text-red-500" />
                  </Button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

import { createClient } from '@/lib/supabase/server'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Package, BookOpen, ShoppingCart, Clock } from 'lucide-react'
import { cn } from '@/lib/utils'
import Link from 'next/link'

export default async function DashboardPage() {
  const supabase = await createClient()
  const { data: { user } } = await supabase.auth.getUser()

  // Fetch statistics
  const [
    ingredientsCount,
    recipesCount,
    shoppingListCount,
    expiringCount
  ] = await Promise.all([
    supabase.from('ingredients').select('id', { count: 'exact', head: true }),
    supabase.from('recipes').select('id', { count: 'exact', head: true }),
    supabase.from('shopping_list').select('id', { count: 'exact', head: true }).eq('purchased', false),
    supabase.from('ingredients')
      .select('id', { count: 'exact', head: true })
      .gte('expiry_date', new Date().toISOString())
      .lte('expiry_date', new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString())
  ])

  const stats = [
    {
      name: 'Total Ingredients',
      value: ingredientsCount.count || 0,
      icon: Package,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      href: '/ingredients',
    },
    {
      name: 'Saved Recipes',
      value: recipesCount.count || 0,
      icon: BookOpen,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      href: '/recipes',
    },
    {
      name: 'Shopping List Items',
      value: shoppingListCount.count || 0,
      icon: ShoppingCart,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
      href: '/shopping-list',
    },
    {
      name: 'Expiring Soon',
      value: expiringCount.count || 0,
      icon: Clock,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
      href: '/ingredients?expiring=true',
    },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome to your Recipe Management System. Here's an overview of your kitchen inventory.
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
        {stats.map((stat) => (
          <Link key={stat.name} href={stat.href}>
            <Card className="hover:shadow-lg transition-shadow cursor-pointer">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-gray-600">
                  {stat.name}
                </CardTitle>
                <div className={cn('p-2 rounded-full', stat.bgColor)}>
                  <stat.icon className={cn('h-5 w-5', stat.color)} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks you might want to do</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Link href="/ingredients" className="block">
              <div className="p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                <h3 className="font-semibold">Add Ingredients</h3>
                <p className="text-sm text-gray-600">Update your kitchen inventory</p>
              </div>
            </Link>
            <Link href="/recipes" className="block">
              <div className="p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                <h3 className="font-semibold">Browse Recipes</h3>
                <p className="text-sm text-gray-600">Find recipes based on your ingredients</p>
              </div>
            </Link>
            <Link href="/chatbot" className="block">
              <div className="p-4 border rounded-lg hover:bg-gray-50 transition-colors">
                <h3 className="font-semibold">Get Recipe Suggestions</h3>
                <p className="text-sm text-gray-600">Ask the AI chef for recommendations</p>
              </div>
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Your latest cooking adventures</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-gray-600">
                Recent activity will appear here once you start using the app.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

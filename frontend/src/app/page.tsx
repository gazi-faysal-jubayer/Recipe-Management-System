import Link from 'next/link'
import { Button } from '@/components/ui/button'

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between text-sm">
        <h1 className="text-4xl font-bold text-center mb-8">
          Welcome to Recipe Management System
        </h1>
        <p className="text-center text-gray-600 mb-12 max-w-2xl mx-auto">
          Manage your ingredients, discover new recipes, and get AI-powered cooking recommendations
          based on what you have at home.
        </p>
        <div className="flex gap-4 justify-center">
          <Link href="/login">
            <Button>Get Started</Button>
          </Link>
          <Link href="/register">
            <Button variant="outline">Create Account</Button>
          </Link>
        </div>
      </div>
    </main>
  )
}

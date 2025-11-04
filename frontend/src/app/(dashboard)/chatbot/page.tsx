'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Send, Bot, User } from 'lucide-react'
import { api } from '@/lib/api/client'
import { toast } from 'react-hot-toast'

interface Message {
  role: 'user' | 'assistant'
  content: string
  recommended_recipes?: any[]
}

export default function ChatbotPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage = input.trim()
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setLoading(true)

    try {
      const response = await api.chatbot.chat({ message: userMessage })
      const { data } = response

      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: data.data.response,
          recommended_recipes: data.data.recommended_recipes || []
        }
      ])
    } catch (error) {
      toast.error('Failed to get response')
      setMessages(prev => [
        ...prev,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.'
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  const quickSuggestions = [
    "What can I cook for dinner?",
    "I want something sweet",
    "Quick Italian recipes",
    "Show me healthy meals",
  ]

  return (
    <div className="h-[calc(100vh-200px)] flex flex-col">
      <div className="mb-4">
        <h1 className="text-3xl font-bold text-gray-900">AI Recipe Assistant</h1>
        <p className="text-gray-600 mt-1">Ask me anything about cooking and recipes!</p>
      </div>

      {/* Chat Container */}
      <Card className="flex-1 flex flex-col overflow-hidden">
        <CardHeader>
          <CardTitle>Chat</CardTitle>
        </CardHeader>
        <CardContent className="flex-1 flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto space-y-4 mb-4">
            {messages.length === 0 ? (
              <div className="text-center py-12 space-y-4">
                <Bot className="h-16 w-16 mx-auto text-gray-400" />
                <div>
                  <p className="text-gray-600 mb-4">
                    Hi! I'm your AI cooking assistant. Ask me about recipes, ingredients, or cooking tips!
                  </p>
                  <div className="flex flex-wrap gap-2 justify-center">
                    {quickSuggestions.map((suggestion, idx) => (
                      <Button
                        key={idx}
                        variant="outline"
                        size="sm"
                        onClick={() => setInput(suggestion)}
                      >
                        {suggestion}
                      </Button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              messages.map((message, idx) => (
                <div key={idx} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`flex gap-2 max-w-[80%] ${message.role === 'user' ? 'flex-row-reverse' : ''}`}>
                    <div className={`p-2 rounded-full ${message.role === 'user' ? 'bg-primary' : 'bg-gray-200'}`}>
                      {message.role === 'user' ? (
                        <User className="h-5 w-5 text-white" />
                      ) : (
                        <Bot className="h-5 w-5 text-gray-700" />
                      )}
                    </div>
                    <div>
                      <div className={`p-3 rounded-lg ${
                        message.role === 'user'
                          ? 'bg-primary text-white'
                          : 'bg-gray-100 text-gray-900'
                      }`}>
                        <p className="whitespace-pre-wrap">{message.content}</p>
                      </div>
                      {message.recommended_recipes && message.recommended_recipes.length > 0 && (
                        <div className="mt-2 space-y-2">
                          {message.recommended_recipes.map((recipe: any, ridx: number) => (
                            <Card key={ridx} className="p-3">
                              <h4 className="font-semibold">{recipe.recipe.title}</h4>
                              <p className="text-sm text-gray-600">
                                Match: {recipe.match_percentage.toFixed(0)}%
                              </p>
                              {recipe.missing_ingredients.length > 0 && (
                                <p className="text-xs text-gray-500 mt-1">
                                  Missing: {recipe.missing_ingredients.join(', ')}
                                </p>
                              )}
                            </Card>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="flex justify-start">
                <div className="flex gap-2 max-w-[80%]">
                  <div className="p-2 rounded-full bg-gray-200">
                    <Bot className="h-5 w-5 text-gray-700" />
                  </div>
                  <div className="p-3 rounded-lg bg-gray-100">
                    <div className="flex gap-1">
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce" />
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100" />
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200" />
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="flex gap-2">
            <Input
              placeholder="Ask me anything..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              disabled={loading}
            />
            <Button onClick={handleSend} disabled={loading || !input.trim()}>
              <Send className="h-4 w-4" />
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

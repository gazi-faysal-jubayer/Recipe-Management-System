import axios, { AxiosInstance, AxiosError } from 'axios'
import { createClient } from '@/lib/supabase/client'
import { toast } from 'react-hot-toast'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  async (config) => {
    const supabase = createClient()
    const { data: { session } } = await supabase.auth.getSession()
    
    if (session?.access_token) {
      config.headers.Authorization = `Bearer ${session.access_token}`
    }
    
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  async (error: AxiosError) => {
    const originalRequest = error.config
    
    if (error.response?.status === 401 && originalRequest) {
      // Token might be expired, try to refresh
      const supabase = createClient()
      const { data: { session }, error: refreshError } = await supabase.auth.refreshSession()
      
      if (!refreshError && session) {
        // Retry with new token
        originalRequest.headers.Authorization = `Bearer ${session.access_token}`
        return apiClient(originalRequest)
      } else {
        // Refresh failed, redirect to login
        window.location.href = '/login'
      }
    }
    
    // Show error toast
    const errorMessage = (error.response?.data as any)?.message || 
                        error.message || 
                        'An error occurred'
    toast.error(errorMessage)
    
    return Promise.reject(error)
  }
)

// API methods
export const api = {
  // Auth
  auth: {
    register: (data: { email: string; password: string; full_name?: string }) =>
      apiClient.post('/api/auth/register/', data),
    login: (data: { email: string; password: string }) =>
      apiClient.post('/api/auth/login/', data),
    logout: (data: { refresh_token: string }) =>
      apiClient.post('/api/auth/logout/', data),
    profile: () =>
      apiClient.get('/api/auth/profile/'),
    updateProfile: (data: { full_name: string }) =>
      apiClient.put('/api/auth/profile/update/', data),
    changePassword: (data: { old_password: string; new_password: string }) =>
      apiClient.post('/api/auth/change-password/', data),
  },
  
  // Ingredients
  ingredients: {
    list: (params?: { category?: string; expiring?: boolean; search?: string }) =>
      apiClient.get('/api/ingredients/', { params }),
    create: (data: any) =>
      apiClient.post('/api/ingredients/', data),
    update: (id: string, data: any) =>
      apiClient.patch(`/api/ingredients/${id}/`, data),
    delete: (id: string) =>
      apiClient.delete(`/api/ingredients/${id}/`),
    bulkUpdate: (data: { operation: string; ingredients: any[] }) =>
      apiClient.post('/api/ingredients/bulk-update/', data),
    categories: () =>
      apiClient.get('/api/ingredients/categories/'),
    importCSV: (file: File) => {
      const formData = new FormData()
      formData.append('file', file)
      return apiClient.post('/api/ingredients/import-csv/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    },
  },
  
  // Recipes
  recipes: {
    list: (params?: { cuisine_type?: string; difficulty?: string; search?: string }) =>
      apiClient.get('/api/recipes/', { params }),
    get: (id: string) =>
      apiClient.get(`/api/recipes/${id}/`),
    create: (data: any) =>
      apiClient.post('/api/recipes/', data),
    update: (id: string, data: any) =>
      apiClient.patch(`/api/recipes/${id}/`, data),
    delete: (id: string) =>
      apiClient.delete(`/api/recipes/${id}/`),
    parseText: (data: { text: string }) =>
      apiClient.post('/api/recipes/parse-text/', data),
    parseImage: (image: File) => {
      const formData = new FormData()
      formData.append('image', image)
      return apiClient.post('/api/recipes/parse-image/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    },
    batchImport: (data: { file?: File; text?: string }) => {
      const formData = new FormData()
      if (data.file) formData.append('file', data.file)
      if (data.text) formData.append('text', data.text)
      return apiClient.post('/api/recipes/batch-import/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    },
    search: (params: any) =>
      apiClient.get('/api/recipes/search/', { params }),
    favorite: (id: string) =>
      apiClient.post(`/api/recipes/${id}/favorite/`),
    unfavorite: (id: string) =>
      apiClient.delete(`/api/recipes/${id}/unfavorite/`),
    favorites: (page?: number) =>
      apiClient.get('/api/recipes/favorites/', { params: { page } }),
  },
  
  // Shopping List
  shoppingList: {
    list: () =>
      apiClient.get('/api/shopping-list/'),
    add: (data: any) =>
      apiClient.post('/api/shopping-list/add/', data),
    toggle: (id: string) =>
      apiClient.patch(`/api/shopping-list/${id}/toggle/`),
    delete: (id: string) =>
      apiClient.delete(`/api/shopping-list/${id}/delete/`),
    addFromRecipe: (recipeId: string) =>
      apiClient.post(`/api/shopping-list/from-recipe/${recipeId}/`),
    clearPurchased: () =>
      apiClient.post('/api/shopping-list/clear-purchased/'),
    addToIngredients: () =>
      apiClient.post('/api/shopping-list/add-to-ingredients/'),
  },
  
  // Chatbot
  chatbot: {
    chat: (data: { message: string; context?: any }) =>
      apiClient.post('/api/chatbot/chat/', data),
    history: (params?: { limit?: number; offset?: number }) =>
      apiClient.get('/api/chatbot/history/', { params }),
    recommend: (data: any) =>
      apiClient.post('/api/chatbot/recommend/', data),
    mealPlan: (data: { days?: number; meals_per_day?: number }) =>
      apiClient.post('/api/chatbot/meal-plan/', data),
  },
  
  // Storage
  storage: {
    uploadRecipeImage: (image: File) => {
      const formData = new FormData()
      formData.append('image', image)
      return apiClient.post('/api/storage/upload/recipe-image/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    },
  },
}

export default apiClient

// API Configuration
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export const api = {
  baseUrl: API_URL,
  
  // Article endpoints
  getArticles: () => `${API_URL}/api/articles`,
  getArticle: (id?: string) => id ? `${API_URL}/api/article/${id}` : `${API_URL}/api/article`,
  generateArticle: () => `${API_URL}/api/generate-article`,
  health: () => `${API_URL}/api/health`,
}


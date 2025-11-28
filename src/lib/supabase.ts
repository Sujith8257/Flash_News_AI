// Supabase client for direct database access from frontend
import { createClient, SupabaseClient } from '@supabase/supabase-js'

// Get Supabase credentials from environment variables
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || ''
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || ''

// Initialize Supabase client
let supabaseClient: SupabaseClient | null = null

if (SUPABASE_URL && SUPABASE_ANON_KEY) {
  try {
    supabaseClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)
    console.log('✅ Supabase client initialized for frontend')
  } catch (error) {
    console.error('❌ Error initializing Supabase client:', error)
  }
} else {
  console.warn('⚠️  Supabase credentials not found. Add VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY to .env')
}

export { supabaseClient }

// Article interface matching the database schema
export interface Article {
  id: string
  title: string
  content: string
  full_text?: string
  created_at: string
  updated_at?: string
  sources: Array<{ name: string; url: string }>
  images: string[]
  topics: string[]
  related_articles: Array<{
    id: string
    title: string
    created_at: string
    similarity?: number
  }>
}

// Fetch all articles from Supabase
export async function fetchArticlesFromSupabase(): Promise<Article[]> {
  if (!supabaseClient) {
    throw new Error('Supabase client not initialized. Please configure VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env file.')
  }

  try {
    const { data, error } = await supabaseClient
      .from('articles')
      .select('*')
      .order('created_at', { ascending: false })

    if (error) {
      console.error('Supabase query error:', error)
      throw new Error(`Failed to fetch articles: ${error.message}`)
    }

    return (data || []) as Article[]
  } catch (error) {
    console.error('Error fetching articles from Supabase:', error)
    throw error
  }
}

// Fetch a single article by ID
export async function fetchArticleFromSupabase(id: string): Promise<Article | null> {
  if (!supabaseClient) {
    throw new Error('Supabase client not initialized. Please configure VITE_SUPABASE_URL and VITE_SUPABASE_ANON_KEY in your .env file.')
  }

  try {
    const { data, error } = await supabaseClient
      .from('articles')
      .select('*')
      .eq('id', id)
      .single()

    if (error) {
      if (error.code === 'PGRST116') {
        // No rows returned - article not found
        return null
      }
      console.error('Supabase query error:', error)
      throw new Error(`Failed to fetch article: ${error.message}`)
    }

    return data as Article
  } catch (error) {
    console.error('Error fetching article from Supabase:', error)
    throw error
  }
}

// Check if Supabase is configured
export function isSupabaseConfigured(): boolean {
  return supabaseClient !== null && SUPABASE_URL !== '' && SUPABASE_ANON_KEY !== ''
}


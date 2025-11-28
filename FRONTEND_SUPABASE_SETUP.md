# Frontend Supabase Setup Guide

This guide explains how to configure the frontend to load articles directly from Supabase without needing the backend API.

## Why Direct Supabase Access?

✅ **Faster**: Direct database queries, no API roundtrip  
✅ **Scalable**: No backend server needed for reading articles  
✅ **Cost-effective**: Reduce backend API calls  
✅ **Real-time**: Can use Supabase real-time subscriptions (future feature)

## Step 1: Get Your Supabase Anon Key

⚠️ **Important**: Use the **ANON key** (not service_role) for the frontend!

1. Go to your Supabase project: https://app.supabase.com
2. Navigate to **Settings** → **API**
3. Find the **anon public** key (not service_role)
4. Copy both:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

## Step 2: Configure Environment Variables

Create or update `.env` in the **root** of your project (not in MODEL folder):

```env
# Supabase Configuration (for direct database access from frontend)
VITE_SUPABASE_URL=https://hznixdhsddcufaogcuyz.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here

# Optional: Backend API (only needed for article generation)
VITE_API_URL=http://localhost:5000
```

**Important Notes:**
- Use `VITE_` prefix for Vite environment variables
- Use the **anon key**, NOT the service_role key
- The anon key is safe to expose in frontend code (RLS policies protect your data)

## Step 3: Install Dependencies

```bash
npm install @supabase/supabase-js
```

Or if using yarn:

```bash
yarn add @supabase/supabase-js
```

## Step 4: Verify RLS Policies

Make sure your Supabase RLS (Row Level Security) policies allow public read access:

1. Go to Supabase Dashboard → **Authentication** → **Policies**
2. Select the `articles` table
3. Verify you have a policy like:
   ```sql
   CREATE POLICY "Allow public read access" ON articles
       FOR SELECT
       USING (true);
   ```

If you ran the SQL schema from `MODEL/supabase_schema.sql`, this policy already exists.

## Step 5: Test the Integration

1. Start your frontend:
   ```bash
   npm run dev
   ```

2. Open the browser console and look for:
   - `✅ Supabase client initialized for frontend` (success)
   - `⚠️  Supabase credentials not found` (check your .env file)

3. Navigate to the feed page - articles should load directly from Supabase!

## How It Works

### Frontend Flow (with Supabase):

```
User Browser
    ↓
Supabase Client (src/lib/supabase.ts)
    ↓
Supabase Database (articles table)
    ↓
Articles displayed in UI
```

### Fallback Flow (if Supabase fails):

```
User Browser
    ↓
Supabase Client (fails)
    ↓
Backend API (api.getArticles())
    ↓
Backend → Supabase/File Storage
    ↓
Articles displayed in UI
```

## Code Structure

### `src/lib/supabase.ts`
- Initializes Supabase client
- Provides `fetchArticlesFromSupabase()` function
- Provides `fetchArticleFromSupabase(id)` function
- Handles errors gracefully

### `src/pages/Feed.tsx`
- Tries Supabase first
- Falls back to backend API if Supabase fails
- Works seamlessly with or without Supabase

### `src/pages/Article.tsx`
- Tries Supabase first
- Falls back to backend API if Supabase fails
- Loads individual articles by ID

## Security Considerations

✅ **Safe**: The anon key is designed for frontend use  
✅ **Protected**: RLS policies control what users can read  
✅ **Read-only**: Frontend can only read articles (not create/update/delete)  
✅ **Backend still needed**: Article generation still requires backend with service_role key

## Troubleshooting

### "Supabase client not initialized"
- Check that `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` are in your `.env` file
- Make sure the `.env` file is in the **root** directory (not MODEL folder)
- Restart your dev server after adding environment variables

### "Failed to fetch articles from Supabase"
- Check browser console for detailed error
- Verify RLS policies allow public read access
- Make sure you're using the **anon key**, not service_role key
- Check that the articles table exists in Supabase

### "No articles found"
- Check Supabase Table Editor to see if articles exist
- Verify articles were saved with the correct structure
- Check browser Network tab to see the actual API response

### Articles load but backend API is still called
- This is normal fallback behavior
- If Supabase is working, it should be used first
- Check browser console for Supabase initialization message

## Environment Variables Summary

### Backend (MODEL/.env):
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key  # For backend operations
SUPABASE_STORAGE_ENABLED=true
```

### Frontend (.env in root):
```env
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key  # For frontend read access
```

## Next Steps

- ✅ Articles load directly from Supabase
- ✅ No backend API needed for reading articles
- ✅ Backend still needed for article generation
- 🔮 Future: Add real-time subscriptions for live article updates

## Benefits Achieved

✅ **Performance**: Faster article loading  
✅ **Scalability**: Frontend doesn't depend on backend for reads  
✅ **Cost**: Reduce backend API calls  
✅ **Reliability**: Direct database connection, fewer failure points


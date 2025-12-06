# Flash News AI

A modern AI-powered news aggregation and generation platform that automatically collects news from multiple sources, verifies facts, and generates comprehensive articles using advanced AI agents.

## 🎯 Project Overview

Flash News AI is a full-stack application that combines real-time news aggregation, AI-powered content generation, and a modern web interface. The system automatically generates news articles every 30 minutes by aggregating content from multiple news sources, fact-checking information, and creating well-structured articles using CrewAI agents powered by Google's Gemini AI.

---

## 🏗️ Architecture & Design Methods

### **Microservices Architecture**
- **Frontend**: React-based SPA (Single Page Application) deployed separately
- **Backend**: Flask REST API with background workers
- **Database**: Supabase PostgreSQL for persistent storage
- **Separation of Concerns**: Clear boundaries between UI, API, and data layers

### **Agent-Based AI System**
- **Multi-Agent Workflow**: Three specialized AI agents working in sequence
  - **News Researcher Agent**: Gathers and ranks news events
  - **Fact Checker Agent**: Verifies information accuracy
  - **Copywriter Agent**: Creates engaging articles
- **CrewAI Framework**: Orchestrates agent collaboration and task execution
- **Tool-Based Architecture**: Custom tools for news fetching and data processing

### **Event-Driven Background Processing**
- **Scheduler Worker**: Background thread that generates articles every 30 minutes
- **Asynchronous Task Execution**: Non-blocking article generation
- **Thread-Based Concurrency**: Python threading for background tasks

---

## 🎨 Frontend Technologies & Methods

### **React 18 with TypeScript**
- **Functional Components**: Modern React hooks-based architecture
- **Type Safety**: Full TypeScript implementation for type checking
- **Component Composition**: Reusable, modular component structure
- **Hooks Usage**:
  - `useState` for local state management
  - `useEffect` for side effects and data fetching
  - Custom hooks for data fetching patterns

### **Vite Build System**
- **Fast Development Server**: HMR (Hot Module Replacement) for instant updates
- **Optimized Production Builds**: Tree-shaking and code splitting
- **Path Aliases**: `@/` alias for cleaner imports
- **Environment Variables**: `VITE_` prefix for client-side env vars

### **React Router v6**
- **Client-Side Routing**: Browser-based navigation without page reloads
- **Dynamic Routes**: Parameterized routes (`/article/:id`)
- **Route Protection**: Conditional rendering based on authentication state
- **Programmatic Navigation**: `useNavigate` hook for navigation

### **Tailwind CSS with Custom Configuration**
- **Utility-First CSS**: Rapid UI development with utility classes
- **Dark Mode Support**: Class-based dark mode toggle
- **Custom Theme**: Black & white minimalist color scheme
- **Responsive Design**: Mobile-first breakpoint system
- **Custom Animations**: `tailwindcss-animate` for smooth transitions
- **CSS Variables**: HSL-based color system for theming

### **shadcn/ui Component Library**
- **Accessible Components**: ARIA-compliant UI components
- **Customizable Design System**: Tailwind-based component architecture
- **Component Variants**: Multiple style variants for buttons, cards, inputs
- **TypeScript Integration**: Fully typed component props

### **Supabase Client Integration**
- **Direct Database Access**: Frontend queries Supabase directly
- **Real-time Capabilities**: Supabase real-time subscriptions (ready for future use)
- **Type-Safe Queries**: TypeScript interfaces matching database schema
- **Error Handling**: Comprehensive error handling for API failures

### **State Management Methods**
- **Local Component State**: `useState` for component-specific data
- **Server State**: Direct Supabase queries with loading/error states
- **No Global State Library**: Lightweight approach without Redux/Zustand
- **Optimistic Updates**: Immediate UI feedback before server confirmation

### **Performance Optimization**
- **Code Splitting**: Route-based code splitting with React.lazy
- **Image Lazy Loading**: `loading="lazy"` attribute for images
- **Memoization**: React.memo for expensive components
- **Debounced Search**: Search input debouncing (ready for implementation)

---

## 🔧 Backend Technologies & Methods

### **Flask REST API**
- **RESTful Endpoints**: Standard HTTP methods (GET, POST)
- **JSON API**: All responses in JSON format
- **Error Handling**: Comprehensive try-catch blocks with proper HTTP status codes
- **Request Validation**: Input validation and sanitization
- **CORS Configuration**: Cross-origin resource sharing for frontend access

### **Flask-CORS Middleware**
- **Origin Whitelist**: Configurable allowed origins
- **Environment-Based CORS**: Different origins for dev/production
- **Security Headers**: Proper CORS headers for API security

### **Background Task Processing**
- **Thread-Based Workers**: Python `threading.Thread` for background tasks
- **Daemon Threads**: Non-blocking background workers
- **Scheduled Execution**: Time-based task scheduling (30-minute intervals)
- **Error Recovery**: Try-catch with logging for resilient background processing

### **Article Generation Pipeline**
1. **News Aggregation**: Fetch from multiple sources simultaneously
2. **Data Normalization**: Standardize article format across sources
3. **Duplicate Detection**: Jaccard similarity algorithm for topic matching
4. **Content Parsing**: Regex-based extraction of title, content, images, sources
5. **Database Persistence**: Save to Supabase with validation

### **Data Processing Methods**
- **Regex Pattern Matching**: Extract images, sources, and content from text
- **JSON Parsing**: Parse and validate JSON structures
- **Text Processing**: Content preview generation (4-5 line summaries)
- **Topic Extraction**: Keyword extraction using frequency analysis
- **Similarity Calculation**: Jaccard similarity for finding related articles

### **Error Handling & Logging**
- **Structured Logging**: Print statements with timestamps and emojis for clarity
- **Exception Handling**: Comprehensive try-catch blocks
- **Error Recovery**: Graceful degradation when services fail
- **Debug Information**: Detailed error messages with stack traces

---

## 🤖 AI/ML Integration Methods

### **CrewAI Multi-Agent Framework**
- **Agent Definition**: Specialized agents with roles, goals, and backstories
- **Task Orchestration**: Sequential task execution with dependencies
- **Tool Integration**: Custom tools for news fetching and data processing
- **LLM Abstraction**: Unified LLM interface for all agents

### **Google Gemini AI Integration**
- **Model Selection**: `gemini-2.0-flash-lite` for optimal free tier usage
- **API Configuration**: Temperature, max_tokens, top_p, frequency/presence penalties
- **Timeout Handling**: 120-second timeout for long-running operations
- **Error Handling**: Graceful handling of API rate limits and errors

### **Custom CrewAI Tools**
- **BaseTool Implementation**: Extend `BaseTool` for custom functionality
- **Tool Descriptions**: Detailed descriptions for LLM tool selection
- **Data Formatting**: JSON output formatting for agent consumption
- **Error Handling**: Try-catch in tool execution

### **News Research Agent**
- **Multi-Source Aggregation**: Fetches from 6+ news sources
- **Event Ranking**: Importance and impact scoring (1-10 scale)
- **Top Event Selection**: Selects top 5 events by combined score
- **Complete Data Collection**: Gathers full content, images, sources, metadata

### **Fact Checker Agent**
- **Cross-Reference Verification**: Compares information across sources
- **Consistency Checking**: Identifies discrepancies
- **Confidence Scoring**: 0-100 confidence scores
- **Verification Status**: VERIFIED, FLAGGED, or PARTIALLY_VERIFIED

### **Copywriter Agent**
- **Article Generation**: 500-1500 word comprehensive articles
- **Formatting Rules**: Structured output with title, content, images, sources
- **Tone Management**: Lively, engaging writing style
- **Source Attribution**: Proper citation formatting

### **Prompt Engineering**
- **Detailed Task Descriptions**: Comprehensive instructions for each agent
- **Expected Output Format**: Clear output structure specifications
- **Critical Requirements**: Emphasis on images, sources, formatting
- **Iterative Refinement**: Prompts refined based on output quality

---

## 📰 News Aggregation Methods

### **Multi-Source News Fetching**
- **NewsAPI**: Top headlines for India via REST API
- **NewsData.io**: Technology news via REST API
- **GDELT**: Global events via query-based API
- **RSS Feeds**: Google News and BBC RSS parsing
- **Reddit API**: Top posts from news subreddits

### **RSS Feed Parsing**
- **feedparser Library**: Parse RSS/Atom feeds
- **Image Extraction**: Extract images from media:content, enclosures, thumbnails
- **Content Normalization**: Standardize article format
- **Error Handling**: Graceful handling of malformed feeds

### **Reddit Integration**
- **JSON API**: Reddit's public JSON API
- **Image Extraction**: Extract from preview images, thumbnails, direct links
- **URL Unescaping**: Handle Reddit's escaped URLs
- **Subreddit Aggregation**: Multiple subreddits (news, worldnews, technology)

### **Data Normalization**
- **Unified Schema**: Standard article format across all sources
- **Field Mapping**: Map source-specific fields to common schema
- **Image URL Extraction**: Multiple methods to find image URLs
- **Source Attribution**: Track original source for each article

### **Image URL Validation**
- **Pattern Matching**: Regex patterns for image URLs
- **Domain Validation**: Check known image hosting domains
- **Extension Checking**: Validate image file extensions
- **URL Cleaning**: Remove trailing punctuation and invalid characters

---

## 💾 Database & Storage Methods

### **Supabase PostgreSQL**
- **Managed PostgreSQL**: Fully managed database service
- **JSONB Columns**: Store arrays and objects (sources, images, topics)
- **Timestamps**: Automatic timestamp management (created_at, updated_at)
- **Indexes**: Optimized queries with proper indexing

### **Database Schema Design**
- **Primary Key**: Timestamp-based unique IDs
- **Text Columns**: Title, content, full_text, content_preview
- **JSONB Columns**: Sources, images, topics, related_articles
- **Timestamps**: Created and updated timestamps

### **Supabase Client Methods**
- **Python Client**: `supabase-py` for backend operations
- **JavaScript Client**: `@supabase/supabase-js` for frontend
- **Upsert Operations**: Insert or update in single operation
- **Query Building**: Fluent query builder API
- **Error Handling**: Comprehensive error handling for database operations

### **Data Persistence Strategy**
- **Direct Database Writes**: Backend writes directly to Supabase
- **Frontend Reads**: Frontend reads directly from Supabase
- **No Intermediate API**: Eliminates unnecessary API layer for reads
- **Service Role Key**: Backend uses service_role key (bypasses RLS)

### **Content Preview Generation**
- **Algorithm**: Extract first 4-5 paragraphs or sentences
- **Character Limits**: Max 100 chars per line, 5 lines total
- **Sentence Boundary Detection**: Smart truncation at sentence boundaries
- **Fallback Methods**: Multiple fallback strategies for preview generation

### **Duplicate Detection**
- **Topic Extraction**: Extract keywords from title and content
- **Jaccard Similarity**: Calculate similarity between article topics
- **Threshold-Based**: 40% similarity threshold for related articles
- **Related Article Linking**: Link similar articles in database

---

## 🔄 Data Flow & Processing Methods

### **Article Generation Workflow**
1. **Trigger**: Scheduled (every 30 min) or manual API call
2. **News Aggregation**: Fetch from all sources in parallel
3. **Event Ranking**: Score and rank events by importance
4. **Top 5 Selection**: Select top 5 events
5. **AI Processing**: CrewAI agents process events
6. **Parsing**: Extract structured data from AI output
7. **Validation**: Validate images, sources, content
8. **Database Save**: Persist to Supabase
9. **Response**: Return article data to client

### **Content Parsing Methods**
- **Title Extraction**: Multiple methods (first line, markdown headers, patterns)
- **Content Extraction**: Remove images and sources sections
- **Source Parsing**: Extract source names and URLs
- **Image Extraction**: Multiple regex patterns for image URLs
- **Text Cleaning**: Remove extra whitespace, format paragraphs

### **Image URL Extraction**
- **Pattern Matching**: 8+ regex patterns for different URL formats
- **Section Parsing**: Extract from "Images:" section
- **JSON Parsing**: Extract from JSON structures
- **Validation**: Validate URLs before saving
- **Deduplication**: Remove duplicate image URLs

### **Error Recovery Methods**
- **Fallback Strategies**: Multiple fallback methods for each operation
- **Graceful Degradation**: Continue operation even if some parts fail
- **Logging**: Comprehensive logging for debugging
- **User Feedback**: Clear error messages for users

---

## 🚀 Deployment Methods

### **Railway Backend Deployment**
- **GitHub Integration**: Automatic deployment from GitHub
- **Root Directory**: Set to `MODEL` folder
- **Environment Variables**: Secure env var management
- **Gunicorn WSGI**: Production WSGI server
- **Process Management**: Automatic process restarts
- **Logging**: Centralized log viewing

### **Vercel Frontend Deployment**
- **GitHub Integration**: Automatic deployment from GitHub
- **Build Configuration**: Automatic Vite build detection
- **Environment Variables**: `VITE_` prefixed variables
- **Edge Network**: Global CDN for fast delivery
- **Preview Deployments**: Automatic preview for PRs

### **Environment Configuration**
- **Backend Variables**:
  - `GEMINI_API_KEY`: Google Gemini API key
  - `SUPABASE_URL`: Supabase project URL
  - `SUPABASE_KEY`: Supabase service_role key
  - `FRONTEND_URL`: Frontend URL for CORS
  - `FLASK_ENV`: Production/development mode
- **Frontend Variables**:
  - `VITE_SUPABASE_URL`: Supabase project URL
  - `VITE_SUPABASE_ANON_KEY`: Supabase anonymous key
  - `VITE_API_URL`: Backend API URL (optional)

### **WSGI Configuration**
- **Gunicorn**: Production WSGI HTTP server
- **Worker Configuration**: Multiple workers for concurrency
- **Timeout Settings**: Appropriate timeouts for AI operations
- **Process Management**: Automatic worker restarts

---

## 🛠️ Development Tools & Methods

### **Package Management**
- **npm**: Node.js package manager for frontend
- **pip**: Python package manager for backend
- **requirements.txt**: Python dependency pinning
- **package.json**: Node.js dependency management

### **Code Quality**
- **TypeScript**: Static type checking
- **ESLint**: JavaScript/TypeScript linting
- **Type Safety**: Full type coverage for frontend
- **Error Handling**: Comprehensive error handling throughout

### **Version Control**
- **Git**: Version control system
- **GitHub**: Repository hosting and CI/CD integration
- **Branch Strategy**: Main branch for production

### **Development Workflow**
- **Hot Reload**: Vite HMR for instant updates
- **Environment Files**: `.env` for local development
- **Local Testing**: Full stack local development setup
- **Debug Logging**: Comprehensive logging for debugging

---

## 📦 Key Dependencies

### **Frontend Dependencies**
- `react` & `react-dom`: UI framework
- `react-router-dom`: Client-side routing
- `@supabase/supabase-js`: Database client
- `tailwindcss`: Utility-first CSS
- `lucide-react`: Icon library
- `clsx` & `tailwind-merge`: Class name utilities

### **Backend Dependencies**
- `flask`: Web framework
- `flask-cors`: CORS middleware
- `gunicorn`: WSGI server
- `crewai[google-genai]`: AI agent framework
- `supabase`: Database client
- `requests`: HTTP client
- `feedparser`: RSS feed parser
- `python-dotenv`: Environment variable management

---

## 🎯 Key Features & Methods

### **Automatic Article Generation**
- **Scheduled Generation**: Every 30 minutes automatically
- **Manual Trigger**: API endpoint for on-demand generation
- **Background Processing**: Non-blocking article generation
- **Error Recovery**: Continues even if one generation fails

### **Multi-Source News Aggregation**
- **6+ News Sources**: NewsAPI, NewsData.io, GDELT, Google News, BBC, Reddit
- **Parallel Fetching**: Simultaneous requests to all sources
- **Data Normalization**: Unified format across sources
- **Source Attribution**: Track original source for each article

### **AI-Powered Content Creation**
- **Multi-Agent System**: Three specialized AI agents
- **Fact Checking**: Automated verification of information
- **Content Quality**: High-quality, engaging articles
- **Source Citation**: Proper attribution and citations

### **Image Management**
- **Automatic Extraction**: Extract images from news sources
- **URL Validation**: Validate image URLs before saving
- **Multiple Fallbacks**: Multiple methods to find images
- **Error Handling**: Graceful handling of missing images

### **Content Preview**
- **Automatic Generation**: 4-5 line summaries
- **Smart Truncation**: Sentence boundary detection
- **Fallback Methods**: Multiple strategies for preview generation
- **Performance**: Fast preview generation

---

## 📚 Project Structure

```
Flash_News_AI/
├── src/                    # Frontend React application
│   ├── components/         # Reusable UI components
│   │   ├── ui/            # shadcn/ui components
│   │   ├── Header.tsx     # Navigation header
│   │   └── Footer.tsx     # Footer component
│   ├── pages/             # Page components
│   │   ├── Home.tsx       # Landing page
│   │   ├── Feed.tsx       # News feed listing
│   │   ├── Article.tsx    # Individual article view
│   │   ├── About.tsx      # About page
│   │   └── Features.tsx   # Features page
│   ├── lib/               # Utility functions
│   │   ├── supabase.ts    # Supabase client & functions
│   │   └── utils.ts       # Helper utilities
│   └── App.tsx            # Main app with routing
├── MODEL/                 # Backend Flask application
│   ├── api.py             # Flask REST API
│   ├── model.py           # CrewAI agents & news fetching
│   ├── wsgi.py            # WSGI entry point
│   ├── requirements.txt   # Python dependencies
│   └── articles/          # Local article storage (backup)
├── public/                # Static assets
├── dist/                  # Production build output
├── package.json           # Frontend dependencies
├── vite.config.ts         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
└── tsconfig.json          # TypeScript configuration
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js 18+** and npm/yarn/pnpm
- **Python 3.11+** and pip
- **Supabase Account** (free tier works)
- **Google Gemini API Key** (free tier available)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd Flash_News_AI
```

2. **Install frontend dependencies**
```bash
npm install
```

3. **Install backend dependencies**
```bash
cd MODEL
pip install -r requirements.txt
```

4. **Set up environment variables**
   - Backend: Create `MODEL/.env` with Supabase and Gemini credentials
   - Frontend: Create `.env` with Supabase credentials

5. **Set up Supabase database**
   - Run SQL schema from `MODEL/supabase_schema.sql`
   - See `MODEL/SUPABASE_SETUP.md` for detailed instructions

6. **Start development servers**
```bash
# Terminal 1: Frontend
npm run dev

# Terminal 2: Backend
cd MODEL
python api.py
```

---

## 📖 Deployment

For detailed deployment instructions, see:
- **[QUICK_DEPLOY.md](./QUICK_DEPLOY.md)** - Fast deployment guide (Railway + Vercel)
- **[DEPLOYMENT.md](./DEPLOYMENT.md)** - Comprehensive deployment guide with multiple options
- **[MODEL/SUPABASE_SETUP.md](./MODEL/SUPABASE_SETUP.md)** - Supabase database setup

### Quick Deployment (10 minutes)

1. **Backend**: Deploy to [Railway](https://railway.app) (set root directory to `MODEL`)
2. **Frontend**: Deploy to [Vercel](https://vercel.com)
3. **Database**: Set up Supabase (see setup guide)
4. **Environment Variables**: Configure all required env vars
5. **Done!** Your app is live 🎉

---

## 🎨 Theme & Design

The application uses a minimalist black & white color scheme:
- **Light Mode**: White background with black text
- **Dark Mode**: Black background with white text
- **Grayscale Only**: No colors for a clean, professional aesthetic
- **Responsive Design**: Mobile-first, works on all screen sizes
- **Accessibility**: ARIA-compliant components with proper contrast

---

## 🔒 Security Considerations

- **Environment Variables**: Sensitive keys stored in environment variables
- **CORS Configuration**: Restricted to known frontend origins
- **Service Role Key**: Backend uses service_role key (secure, server-side only)
- **Input Validation**: All inputs validated and sanitized
- **Error Messages**: Generic error messages to prevent information leakage

---

## 📝 License

This project is open source and available for use and modification.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

# Flash News AI

A modern React application built with shadcn/ui components and a black & white theme.

## Features

- React + TypeScript + Vite
- shadcn/ui components
- Tailwind CSS with black & white theme
- React Router for navigation
- Supabase integration for authentication

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn/pnpm

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create a `.env` file in the root directory:
```
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

3. Start the development server:
```bash
npm run dev
```

4. Build for production:
```bash
npm run build
```

## Project Structure

```
src/
├── components/        # Reusable components
│   ├── ui/          # shadcn/ui components
│   ├── Header.tsx   # Navigation header
│   └── Footer.tsx   # Footer component
├── pages/           # Page components
│   ├── Home.tsx
│   ├── Feed.tsx
│   ├── Article.tsx
│   ├── SignIn.tsx
│   ├── SignUp.tsx
│   ├── About.tsx
│   └── Features.tsx
├── lib/             # Utility functions
└── App.tsx          # Main app component with routing
```

## Theme

The application uses a black and white color scheme:
- Light mode: White background with black text
- Dark mode: Black background with white text
- All colors are grayscale for a minimalist aesthetic

## Technologies

- React 18
- TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- React Router
- Supabase


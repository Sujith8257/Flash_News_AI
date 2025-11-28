import { Link, useLocation } from "react-router-dom"
import { Button } from "./ui/button"

export function Header() {
  const location = useLocation()
  
  const isActive = (path: string) => location.pathname === path

  return (
    <header className="sticky top-0 z-50 bg-background/80 backdrop-blur-sm border-b">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-20">
          <div className="flex items-center gap-3">
            <Link to="/feed">
              <img src="/logo1.png" alt="Flash News AI logo" className="w-10 h-10 object-contain" />
            </Link>
            <h2 className="text-2xl font-bold">Flash News AI</h2>
          </div>
          <nav className="hidden md:flex items-center gap-8">
            <Link
              to="/"
              className={`text-lg transition-colors ${
                isActive("/") 
                  ? "font-semibold" 
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Home
            </Link>
            <Link
              to="/features"
              className={`text-lg transition-colors ${
                isActive("/features") 
                  ? "font-semibold" 
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              Features
            </Link>
            <Link
              to="/about"
              className={`text-lg transition-colors ${
                isActive("/about") 
                  ? "font-semibold" 
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              About
            </Link>
          </nav>
          <div className="flex items-center gap-4">
            <Button variant="outline" asChild>
              <Link to="/signin">Login</Link>
            </Button>
            <Button asChild>
              <Link to="/signup">Sign Up</Link>
            </Button>
          </div>
        </div>
      </div>
    </header>
  )
}


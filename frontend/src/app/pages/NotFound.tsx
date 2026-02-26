import { Link, useNavigate } from "react-router";
import { Button } from "../components/ui/button";
import { Wallet, Home, ArrowLeft, User } from "lucide-react";
import { useApp } from "../context/AppContext";
import { ThemeToggle } from "../components/ThemeToggle";

export function NotFound() {
  const navigate = useNavigate();
  const { isAuthenticated } = useApp();
  const HomeLink = isAuthenticated ? "/dashboard" : "/";

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <nav className="w-full border-b border-border bg-card">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <ThemeToggle />
            <Link to="/" className="flex items-center gap-2">
              <div className="rounded-lg bg-primary p-2">
                <Wallet className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="text-lg font-semibold">Prognosis AI</span>
            </Link>
          </div>
        </div>
      </nav>

      <div className="flex-1 flex items-center justify-center px-4">
        <div className="text-center space-y-6 max-w-md">
          <div className="space-y-2">
            <p className="text-8xl font-bold text-primary/30 select-none">
              404
            </p>
            <h1 className="text-3xl font-semibold">Page not found</h1>
            <p className="text-muted-foreground">
              The page you're looking for doesn't exist or has been moved.
            </p>
          </div>
          <div className="flex items-center justify-center gap-3 pt-2">
            {isAuthenticated && (
              <Button
                variant="outline"
                onClick={() => navigate(-1)}
                className="gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Go Back
              </Button>
            )}
            <Button asChild className="gap-2">
              <Link to={HomeLink}>
                <Home className="h-4 w-4" />
                Home
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}

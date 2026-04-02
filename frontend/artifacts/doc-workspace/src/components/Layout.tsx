import { Sidebar } from "./Sidebar";
import { ReactNode, useState } from "react";
import { Menu, X, LogIn } from "lucide-react";
import { Link, useLocation } from "wouter";
import { cn } from "@/lib/utils";
import { BrainCircuit } from "lucide-react";
import { useAuth } from "@/context/AuthContext";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [location] = useLocation();
  const { user, openAuthModal } = useAuth();

  const navItems = [
    { href: "/", label: "Dashboard" },
    { href: "/documents", label: "Documents" },
    { href: "/search", label: "Semantic Search" },
    { href: "/ask", label: "Ask VectorLearn" },
    { href: "/community", label: "Community" },
  ];

  return (
    <div className="flex min-h-screen bg-background text-foreground font-sans">
      <Sidebar />

      {/* Mobile Header */}
      <div className="md:hidden fixed top-0 left-0 right-0 h-16 border-b border-border bg-background/80 backdrop-blur-md z-50 flex items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-primary to-blue-400 flex items-center justify-center">
            <BrainCircuit className="w-5 h-5 text-white" />
          </div>
          <span className="font-display font-bold">VectorLearn</span>
        </Link>
        <div className="flex items-center gap-2">
          {!user && (
            <button
              onClick={() => openAuthModal("signin")}
              className="flex items-center gap-1 text-sm text-primary font-medium px-3 py-1.5 rounded-lg border border-primary/30 hover:bg-primary/10 transition-colors"
            >
              <LogIn className="w-4 h-4" />
              Sign In
            </button>
          )}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 text-muted-foreground hover:text-foreground rounded-md"
          >
            {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 top-16 bg-background/95 backdrop-blur-sm z-40 p-4 flex flex-col gap-2">
          {navItems.map(item => (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setMobileMenuOpen(false)}
              className={cn(
                "p-4 rounded-xl font-medium text-lg",
                location === item.href ? "bg-primary/20 text-primary" : "text-muted-foreground hover:bg-white/5"
              )}
            >
              {item.label}
            </Link>
          ))}
        </div>
      )}

      <main className="flex-1 w-full min-w-0 pt-16 md:pt-0 flex flex-col">
        {children}
      </main>
    </div>
  );
}

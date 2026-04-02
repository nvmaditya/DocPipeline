import { createContext, useContext, useState, useEffect, ReactNode } from "react";

export type User = {
  name: string;
  email: string;
  avatar: string;
};

type AuthContextType = {
  user: User | null;
  token: string | null;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (name: string, email: string, password: string) => Promise<void>;
  signOut: () => void;
  showAuthModal: boolean;
  openAuthModal: (mode?: "signin" | "signup") => void;
  closeAuthModal: () => void;
  authMode: "signin" | "signup";
  setAuthMode: (mode: "signin" | "signup") => void;
};

const AuthContext = createContext<AuthContextType | null>(null);

const TOKEN_KEY = "docmind_access_token";

function userFromEmail(email: string): User {
  return {
    name: email.split("@")[0].replace(/[._]/g, " ").replace(/\b\w/g, (c) => c.toUpperCase()),
    email,
    avatar: `https://api.dicebear.com/7.x/initials/svg?seed=${encodeURIComponent(email)}`,
  };
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [authMode, setAuthMode] = useState<"signin" | "signup">("signin");

  // Restore session from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(TOKEN_KEY);
    if (stored) {
      setToken(stored);
      // Validate token by calling /me
      fetch("/api/auth/me", {
        headers: { Authorization: `Bearer ${stored}` },
      })
        .then((res) => {
          if (res.ok) return res.json();
          throw new Error("invalid");
        })
        .then((data: { email?: string; user_id?: string }) => {
          if (data.email) {
            setUser(userFromEmail(data.email));
          }
        })
        .catch(() => {
          localStorage.removeItem(TOKEN_KEY);
          setToken(null);
        });
    }
  }, []);

  const signIn = async (email: string, password: string) => {
    const res = await fetch("/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(err.detail || "Login failed");
    }

    const data = await res.json();
    const accessToken = data.access_token;

    localStorage.setItem(TOKEN_KEY, accessToken);
    setToken(accessToken);
    setUser(userFromEmail(email));
    setShowAuthModal(false);
  };

  const signUp = async (_name: string, email: string, password: string) => {
    const res = await fetch("/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Registration failed" }));
      throw new Error(err.detail || "Registration failed");
    }

    // Auto-login after registration
    await signIn(email, password);
  };

  const signOut = () => {
    if (token) {
      fetch("/api/auth/logout", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
      }).catch(() => {});
    }
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setUser(null);
  };

  const openAuthModal = (mode: "signin" | "signup" = "signin") => {
    setAuthMode(mode);
    setShowAuthModal(true);
  };

  const closeAuthModal = () => setShowAuthModal(false);

  return (
    <AuthContext.Provider
      value={{ user, token, signIn, signUp, signOut, showAuthModal, openAuthModal, closeAuthModal, authMode, setAuthMode }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}

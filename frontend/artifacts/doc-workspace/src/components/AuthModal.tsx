import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, BrainCircuit, Mail, Lock, User, Eye, EyeOff, Loader2, Github, Chrome } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { cn } from "@/lib/utils";

export function AuthModal() {
  const { showAuthModal, closeAuthModal, authMode, setAuthMode, signIn, signUp } = useAuth();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const reset = () => {
    setName("");
    setEmail("");
    setPassword("");
    setError("");
    setShowPassword(false);
  };

  const switchMode = (mode: "signin" | "signup") => {
    setAuthMode(mode);
    reset();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (!email || !password) { setError("Please fill in all fields."); return; }
    if (authMode === "signup" && !name) { setError("Please enter your name."); return; }
    if (password.length < 6) { setError("Password must be at least 6 characters."); return; }

    setIsLoading(true);
    try {
      if (authMode === "signin") {
        await signIn(email, password);
      } else {
        await signUp(name, email, password);
      }
      reset();
    } catch (err: any) {
      setError(err?.message || "Something went wrong. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AnimatePresence>
      {showAuthModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={closeAuthModal}
            className="absolute inset-0 bg-black/70 backdrop-blur-sm"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="relative w-full max-w-md bg-card border border-border rounded-3xl shadow-2xl overflow-hidden"
          >
            {/* Gradient top bar */}
            <div className="h-1 w-full bg-gradient-to-r from-primary via-blue-400 to-purple-500" />

            <div className="p-8">
              {/* Close button */}
              <button
                onClick={closeAuthModal}
                className="absolute top-6 right-6 p-2 text-muted-foreground hover:text-foreground hover:bg-white/5 rounded-xl transition-colors"
              >
                <X className="w-5 h-5" />
              </button>

              {/* Logo */}
              <div className="flex items-center gap-3 mb-8">
                <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-primary to-blue-400 flex items-center justify-center shadow-lg shadow-primary/25">
                  <BrainCircuit className="w-6 h-6 text-white" />
                </div>
                <span className="font-bold text-xl text-foreground">VectorLearn</span>
              </div>

              {/* Title */}
              <div className="mb-8">
                <h2 className="text-2xl font-bold text-foreground mb-1">
                  {authMode === "signin" ? "Welcome back" : "Create your account"}
                </h2>
                <p className="text-muted-foreground text-sm">
                  {authMode === "signin"
                    ? "Sign in to access your document workspace"
                    : "Start building your personal knowledge base"}
                </p>
              </div>

              {/* Tab toggle */}
              <div className="flex bg-muted/50 rounded-xl p-1 mb-8 border border-border/50">
                <button
                  onClick={() => switchMode("signin")}
                  className={cn(
                    "flex-1 py-2 text-sm font-semibold rounded-lg transition-all",
                    authMode === "signin"
                      ? "bg-primary text-primary-foreground shadow-md"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  Sign In
                </button>
                <button
                  onClick={() => switchMode("signup")}
                  className={cn(
                    "flex-1 py-2 text-sm font-semibold rounded-lg transition-all",
                    authMode === "signup"
                      ? "bg-primary text-primary-foreground shadow-md"
                      : "text-muted-foreground hover:text-foreground"
                  )}
                >
                  Sign Up
                </button>
              </div>

              {/* Social buttons */}
              <div className="grid grid-cols-2 gap-3 mb-6">
                <button className="flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-border/50 rounded-xl py-2.5 text-sm font-medium text-foreground transition-colors">
                  <Github className="w-4 h-4" />
                  GitHub
                </button>
                <button className="flex items-center justify-center gap-2 bg-white/5 hover:bg-white/10 border border-border/50 rounded-xl py-2.5 text-sm font-medium text-foreground transition-colors">
                  <Chrome className="w-4 h-4" />
                  Google
                </button>
              </div>

              <div className="flex items-center gap-3 mb-6">
                <div className="flex-1 h-px bg-border/50" />
                <span className="text-xs text-muted-foreground">or continue with email</span>
                <div className="flex-1 h-px bg-border/50" />
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="space-y-4">
                <AnimatePresence mode="wait">
                  {authMode === "signup" && (
                    <motion.div
                      key="name-field"
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      transition={{ duration: 0.2 }}
                    >
                      <div className="relative">
                        <User className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                        <input
                          type="text"
                          placeholder="Full name"
                          value={name}
                          onChange={(e) => setName(e.target.value)}
                          className="w-full bg-muted/40 border border-border/50 focus:border-primary/50 rounded-xl py-3 pl-11 pr-4 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none transition-colors"
                        />
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                <div className="relative">
                  <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input
                    type="email"
                    placeholder="Email address"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="w-full bg-muted/40 border border-border/50 focus:border-primary/50 rounded-xl py-3 pl-11 pr-4 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none transition-colors"
                  />
                </div>

                <div className="relative">
                  <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                  <input
                    type={showPassword ? "text" : "password"}
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full bg-muted/40 border border-border/50 focus:border-primary/50 rounded-xl py-3 pl-11 pr-11 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none transition-colors"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  >
                    {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>

                {error && (
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    className="text-sm text-destructive bg-destructive/10 border border-destructive/20 rounded-xl px-4 py-2"
                  >
                    {error}
                  </motion.p>
                )}

                {authMode === "signin" && (
                  <div className="text-right">
                    <button type="button" className="text-xs text-primary hover:underline">
                      Forgot password?
                    </button>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-3 rounded-xl transition-all shadow-lg shadow-primary/20 disabled:opacity-70 flex items-center justify-center gap-2"
                >
                  {isLoading && <Loader2 className="w-4 h-4 animate-spin" />}
                  {authMode === "signin" ? "Sign In" : "Create Account"}
                </button>
              </form>

              {authMode === "signup" && (
                <p className="text-center text-xs text-muted-foreground mt-4">
                  By creating an account, you agree to our{" "}
                  <button className="text-primary hover:underline">Terms of Service</button> and{" "}
                  <button className="text-primary hover:underline">Privacy Policy</button>.
                </p>
              )}
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}

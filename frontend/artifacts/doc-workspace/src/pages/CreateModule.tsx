import { useState } from "react";
import { Layout } from "@/components/Layout";
import { useLocation } from "wouter";
import { motion } from "framer-motion";
import { useAuth } from "@/context/AuthContext";
import { BookPlus, Loader2, AlertCircle } from "lucide-react";

export default function CreateModule() {
  const [topic, setTopic] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [, navigate] = useLocation();
  const { user, token, openAuthModal } = useAuth();

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) return;

    if (!user) {
      openAuthModal("signup");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch("/api/community/modules", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify({ topic: topic.trim() })
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || errData.error || "Failed to create module");
      }

      await res.json();
      
      // Navigate to Community tab when the new DB is created
      navigate(`/community`);
      
    } catch (err: any) {
      setError(err.message || "An unexpected error occurred.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <div className="flex-1 overflow-y-auto">
        <div className="relative border-b border-border/50 bg-gradient-to-b from-primary/5 to-background px-6 md:px-12 py-12 md:py-16">
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-0 right-1/4 w-64 h-64 bg-primary/5 rounded-full blur-3xl" />
          </div>
          <div className="relative max-w-3xl">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs font-bold uppercase tracking-widest text-primary bg-primary/10 px-3 py-1 rounded-full border border-primary/20">
                Web Extractor
              </span>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Create <span className="text-primary">Custom Module</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl">
              Enter a topic and VectorLearn will autonomously research the web, extract content, and build a dedicated vector database for you to chat with.
            </p>
          </div>
        </div>

        <div className="px-6 md:px-12 py-12 max-w-2xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-card border border-border shadow-2xl rounded-2xl p-8"
          >
            <form onSubmit={handleCreate} className="space-y-6">
              <div>
                <label htmlFor="topic" className="block text-sm font-medium text-foreground mb-2">
                  What would you like to learn about?
                </label>
                <input
                  id="topic"
                  type="text"
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="e.g. History of Quantum Mechanics"
                  className="w-full bg-background border border-border rounded-xl py-3 px-4 text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all"
                  disabled={loading}
                  required
                />
                <p className="text-xs text-muted-foreground mt-2">
                  Be specific! This will be used as the search query for the extraction pipeline.
                </p>
              </div>

              {error && (
                <div className="flex items-center gap-2 text-sm text-red-400 bg-red-400/10 border border-red-400/20 rounded-xl p-4">
                  <AlertCircle className="w-5 h-5 shrink-0" />
                  <p>{error}</p>
                </div>
              )}

              <button
                type="submit"
                disabled={loading || !topic.trim()}
                className="w-full flex items-center justify-center gap-2 bg-primary hover:bg-primary/90 text-primary-foreground font-semibold py-3 px-4 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Synthesizing Module... (This may take 30-60 seconds)
                  </>
                ) : (
                  <>
                    <BookPlus className="w-5 h-5" />
                    Generate & Index Module
                  </>
                )}
              </button>
            </form>
          </motion.div>
        </div>
      </div>
    </Layout>
  );
}

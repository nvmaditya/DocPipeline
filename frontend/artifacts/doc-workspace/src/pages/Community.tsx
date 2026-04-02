import { useState, useEffect } from "react";
import { Layout } from "@/components/Layout";
import { useLocation } from "wouter";
import { motion } from "framer-motion";
import { useChatContext } from "@/context/ChatContext";
import { useAuth } from "@/context/AuthContext";
import {
  BookOpen,
  Users,
  MessageSquare,
  ChevronRight,
  Search,
  Database,
  FileText,
  Loader2,
  AlertCircle,
  Layers,
  RefreshCw,
} from "lucide-react";
import { cn } from "@/lib/utils";

type CommunityDatabase = {
  database_id: string;
  title: string;
  source_file: string;
  documents: number;
  chunks: number;
};

// Assign a consistent visual style to each book based on its index
const bookStyles = [
  { color: "text-blue-400", gradientFrom: "from-blue-500/20", gradientTo: "to-indigo-500/10" },
  { color: "text-cyan-400", gradientFrom: "from-cyan-500/20", gradientTo: "to-blue-500/10" },
  { color: "text-emerald-400", gradientFrom: "from-emerald-500/20", gradientTo: "to-green-500/10" },
  { color: "text-violet-400", gradientFrom: "from-violet-500/20", gradientTo: "to-purple-500/10" },
  { color: "text-amber-400", gradientFrom: "from-amber-500/20", gradientTo: "to-orange-500/10" },
  { color: "text-rose-400", gradientFrom: "from-rose-500/20", gradientTo: "to-pink-500/10" },
  { color: "text-teal-400", gradientFrom: "from-teal-500/20", gradientTo: "to-cyan-500/10" },
  { color: "text-pink-400", gradientFrom: "from-pink-500/20", gradientTo: "to-rose-500/10" },
  { color: "text-lime-400", gradientFrom: "from-lime-500/20", gradientTo: "to-emerald-500/10" },
  { color: "text-orange-400", gradientFrom: "from-orange-500/20", gradientTo: "to-amber-500/10" },
];

function getBookStyle(index: number) {
  return bookStyles[index % bookStyles.length];
}

function formatTitle(title: string): string {
  // Convert database slug-style titles to readable names
  return title
    .replace(/([a-z])([A-Z])/g, "$1 $2") // camelCase
    .replace(/[-_]+/g, " ")              // dashes/underscores
    .replace(/\b\w/g, (c) => c.toUpperCase()); // capitalize words
}

function formatNumber(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return n.toString();
}

export default function Community() {
  const [databases, setDatabases] = useState<CommunityDatabase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [, navigate] = useLocation();
  const { openChatFromCommunity } = useChatContext();
  const { user, token, openAuthModal } = useAuth();

  const fetchDatabases = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/community/databases", {
        headers: user && token
          ? { Authorization: `Bearer ${token}` }
          : {},
      });
      if (!res.ok) {
        if (res.status === 401) {
          setError("Sign in to access community knowledge bases.");
        } else {
          setError("Failed to load community databases.");
        }
        return;
      }
      const data = await res.json();
      setDatabases(data.databases || []);
    } catch {
      setError("Unable to connect to the server.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDatabases();
  }, [user]);

  const filtered = databases.filter((db) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return (
      db.title.toLowerCase().includes(q) ||
      db.database_id.toLowerCase().includes(q)
    );
  });

  const totalChunks = databases.reduce((sum, db) => sum + db.chunks, 0);

  const handleStartChat = (db: CommunityDatabase) => {
    if (!user) {
      openAuthModal("signup");
      return;
    }
    openChatFromCommunity(formatTitle(db.title), db.database_id);
    navigate("/ask");
  };

  return (
    <Layout>
      <div className="flex-1 overflow-y-auto">
        {/* Hero */}
        <div className="relative border-b border-border/50 bg-gradient-to-b from-primary/5 to-background px-6 md:px-12 py-12 md:py-16">
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-0 left-1/4 w-64 h-64 bg-primary/5 rounded-full blur-3xl" />
            <div className="absolute top-10 right-1/4 w-48 h-48 bg-blue-500/5 rounded-full blur-3xl" />
          </div>
          <div className="relative max-w-3xl">
            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs font-bold uppercase tracking-widest text-primary bg-primary/10 px-3 py-1 rounded-full border border-primary/20">
                Community
              </span>
              {!loading && (
                <span className="text-xs text-muted-foreground">
                  {databases.length} knowledge {databases.length === 1 ? "base" : "bases"} available
                </span>
              )}
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-4">
              Community <span className="text-primary">Knowledge Bases</span>
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl">
              Explore our curated library of indexed books. Each book has been processed into a searchable vector database — start a chat to get tutoring and explanations.
            </p>
          </div>
        </div>

        <div className="px-6 md:px-12 py-8 space-y-8">
          {/* Search */}
          <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
            <div className="relative w-full sm:w-72">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search knowledge bases..."
                className="w-full bg-card border border-border rounded-xl py-2 pl-9 pr-4 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary/50 transition-colors"
              />
            </div>
            {!loading && !error && (
              <button
                onClick={fetchDatabases}
                className="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground border border-border rounded-lg px-3 py-1.5 transition-colors"
              >
                <RefreshCw className="w-3 h-3" /> Refresh
              </button>
            )}
          </div>

          {/* Stats */}
          {!loading && !error && databases.length > 0 && (
            <div className="grid grid-cols-3 gap-4">
              {[
                { icon: Database, label: "Knowledge Bases", value: `${databases.length}`, color: "text-primary" },
                { icon: Layers, label: "Total Chunks", value: formatNumber(totalChunks), color: "text-emerald-400" },
                { icon: FileText, label: "Source Documents", value: `${databases.reduce((s, d) => s + d.documents, 0)}`, color: "text-amber-400" },
              ].map((stat) => (
                <div key={stat.label} className="bg-card border border-border rounded-2xl p-4 flex items-center gap-3">
                  <stat.icon className={cn("w-5 h-5 shrink-0", stat.color)} />
                  <div className="min-w-0">
                    <p className="text-xs text-muted-foreground truncate">{stat.label}</p>
                    <p className="font-bold text-foreground truncate">{stat.value}</p>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Loading state */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-20">
              <Loader2 className="w-10 h-10 text-primary animate-spin mb-4" />
              <p className="text-muted-foreground">Loading community knowledge bases...</p>
            </div>
          )}

          {/* Error state */}
          {!loading && error && (
            <div className="flex flex-col items-center justify-center py-20">
              <AlertCircle className="w-10 h-10 text-red-400/50 mb-4" />
              <p className="text-muted-foreground mb-4">{error}</p>
              <button
                onClick={fetchDatabases}
                className="bg-primary/10 text-primary border border-primary/20 px-4 py-2 rounded-xl text-sm font-medium hover:bg-primary hover:text-primary-foreground transition-all"
              >
                Try Again
              </button>
            </div>
          )}

          {/* Database Grid */}
          {!loading && !error && (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {filtered.map((db, idx) => {
                const style = getBookStyle(idx);
                return (
                  <motion.div
                    key={db.database_id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.06 }}
                    className="group relative bg-card border border-border hover:border-primary/30 rounded-2xl overflow-hidden transition-all hover:shadow-xl hover:shadow-black/10"
                  >
                    <div className={cn("absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-100 transition-opacity", style.gradientFrom, style.gradientTo)} />

                    <div className="relative p-6">
                      {/* Header */}
                      <div className="flex items-start gap-4 mb-4">
                        <div className={cn("w-12 h-12 rounded-2xl bg-white/5 border border-white/10 flex items-center justify-center shrink-0", style.color)}>
                          <BookOpen className="w-6 h-6" />
                        </div>
                        <div className="min-w-0">
                          <h3 className="font-bold text-foreground text-lg leading-tight">{formatTitle(db.title)}</h3>
                          <p className="text-xs text-muted-foreground mt-0.5">Vector Database</p>
                        </div>
                      </div>

                      <p className="text-sm text-muted-foreground leading-relaxed mb-4">
                        Indexed from <span className="font-medium text-foreground/80">{db.source_file.split(/[/\\]/).pop()}</span> — contains {formatNumber(db.chunks)} searchable knowledge chunks across {db.documents} source {db.documents === 1 ? "document" : "documents"}.
                      </p>

                      {/* Metadata chips */}
                      <div className="flex flex-wrap gap-1.5 mb-5">
                        <span className="text-[10px] font-semibold uppercase tracking-wider bg-white/5 border border-white/10 px-2 py-0.5 rounded-full text-muted-foreground">
                          {formatNumber(db.chunks)} chunks
                        </span>
                        <span className="text-[10px] font-semibold uppercase tracking-wider bg-white/5 border border-white/10 px-2 py-0.5 rounded-full text-muted-foreground">
                          {db.documents} {db.documents === 1 ? "doc" : "docs"}
                        </span>
                        <span className="text-[10px] font-semibold uppercase tracking-wider bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full text-emerald-400">
                          Indexed
                        </span>
                      </div>

                      {/* Stats row */}
                      <div className="flex items-center gap-4 text-xs text-muted-foreground mb-5 border-t border-border/50 pt-4">
                        <span className="flex items-center gap-1">
                          <Database className="w-3 h-3 text-primary" />
                          FAISS Index
                        </span>
                        <span className="flex items-center gap-1">
                          <Layers className="w-3 h-3" />
                          {formatNumber(db.chunks)} vectors
                        </span>
                      </div>

                      {/* Action buttons */}
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleStartChat(db)}
                          className="flex-1 flex items-center justify-center gap-2 bg-primary/10 hover:bg-primary text-primary hover:text-primary-foreground border border-primary/20 hover:border-primary font-semibold text-sm py-2.5 rounded-xl transition-all group/btn"
                        >
                          <MessageSquare className="w-4 h-4" />
                          Ask Doubt
                        </button>
                        <button
                          onClick={() => navigate(`/book-modules/${db.database_id}`)}
                          className="flex-1 flex items-center justify-center gap-2 bg-emerald-500/10 hover:bg-emerald-500 text-emerald-400 hover:text-white border border-emerald-500/20 hover:border-emerald-500 font-semibold text-sm py-2.5 rounded-xl transition-all group/btn"
                        >
                          <Layers className="w-4 h-4" />
                          View Modules
                          <ChevronRight className="w-4 h-4 opacity-0 -translate-x-1 group-hover/btn:opacity-100 group-hover/btn:translate-x-0 transition-all" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}

          {!loading && !error && filtered.length === 0 && databases.length > 0 && (
            <div className="text-center py-20">
              <BookOpen className="w-12 h-12 text-muted-foreground/30 mx-auto mb-4" />
              <p className="text-muted-foreground">No knowledge bases match your search.</p>
            </div>
          )}

          {!loading && !error && databases.length === 0 && (
            <div className="text-center py-20">
              <Database className="w-12 h-12 text-muted-foreground/30 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-foreground mb-2">No Knowledge Bases Yet</h3>
              <p className="text-muted-foreground max-w-md mx-auto">
                Community knowledge bases haven't been created yet. Run the bootstrap script to index books from the Books folder.
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

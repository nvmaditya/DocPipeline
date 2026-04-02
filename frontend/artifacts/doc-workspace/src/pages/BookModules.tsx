import { useState, useEffect } from "react";
import { Layout } from "@/components/Layout";
import { useLocation, useRoute } from "wouter";
import { motion } from "framer-motion";
import { useChatContext } from "@/context/ChatContext";
import { useAuth } from "@/context/AuthContext";
import {
  BookOpen,
  MessageSquare,
  ChevronRight,
  Loader2,
  AlertCircle,
  Layers,
  ArrowLeft,
  Hash,
} from "lucide-react";
import { cn } from "@/lib/utils";

type TopicEntry = {
  topic_id: number;
  name: string;
  chunk_count: number;
  chunk_ids: number[];
};

type TopicsResponse = {
  database_id: string;
  title: string;
  topics: TopicEntry[];
};

const topicColors = [
  { bg: "bg-blue-500/10", border: "border-blue-500/20", text: "text-blue-400", hover: "hover:bg-blue-500 hover:border-blue-500 hover:text-white" },
  { bg: "bg-emerald-500/10", border: "border-emerald-500/20", text: "text-emerald-400", hover: "hover:bg-emerald-500 hover:border-emerald-500 hover:text-white" },
  { bg: "bg-violet-500/10", border: "border-violet-500/20", text: "text-violet-400", hover: "hover:bg-violet-500 hover:border-violet-500 hover:text-white" },
  { bg: "bg-amber-500/10", border: "border-amber-500/20", text: "text-amber-400", hover: "hover:bg-amber-500 hover:border-amber-500 hover:text-white" },
  { bg: "bg-rose-500/10", border: "border-rose-500/20", text: "text-rose-400", hover: "hover:bg-rose-500 hover:border-rose-500 hover:text-white" },
  { bg: "bg-cyan-500/10", border: "border-cyan-500/20", text: "text-cyan-400", hover: "hover:bg-cyan-500 hover:border-cyan-500 hover:text-white" },
  { bg: "bg-pink-500/10", border: "border-pink-500/20", text: "text-pink-400", hover: "hover:bg-pink-500 hover:border-pink-500 hover:text-white" },
  { bg: "bg-teal-500/10", border: "border-teal-500/20", text: "text-teal-400", hover: "hover:bg-teal-500 hover:border-teal-500 hover:text-white" },
];

function formatTitle(title: string): string {
  return title
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/[-_]+/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

export default function BookModules() {
  const [, params] = useRoute("/book-modules/:databaseId");
  const databaseId = params?.databaseId ?? "";

  const [data, setData] = useState<TopicsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [, navigate] = useLocation();
  const { openChatFromCommunity } = useChatContext();
  const { user, token, openAuthModal } = useAuth();

  useEffect(() => {
    if (!databaseId) return;
    setLoading(true);
    setError(null);

    fetch(`/api/community/databases/${databaseId}/topics`, {
      headers: user && token ? { Authorization: `Bearer ${token}` } : {},
    })
      .then(async (res) => {
        if (!res.ok) {
          if (res.status === 401) throw new Error("Sign in to view modules.");
          throw new Error("Failed to load topics.");
        }
        return res.json();
      })
      .then((d: TopicsResponse) => setData(d))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [databaseId, user]);

  const handleAskAboutTopic = (topicName: string) => {
    if (!user) {
      openAuthModal("signup");
      return;
    }
    openChatFromCommunity(
      `${formatTitle(data?.title ?? databaseId)} — ${topicName}`,
      databaseId,
    );
    navigate("/ask");
  };

  const totalChunks = data?.topics.reduce((s, t) => s + t.chunk_count, 0) ?? 0;

  return (
    <Layout>
      <div className="flex-1 overflow-y-auto">
        {/* Hero */}
        <div className="relative border-b border-border/50 bg-gradient-to-b from-emerald-500/5 to-background px-6 md:px-12 py-12 md:py-16">
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute top-0 left-1/4 w-64 h-64 bg-emerald-500/5 rounded-full blur-3xl" />
          </div>

          <div className="relative max-w-3xl">
            <button
              onClick={() => navigate("/community")}
              className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Community
            </button>

            <div className="flex items-center gap-2 mb-4">
              <span className="text-xs font-bold uppercase tracking-widest text-emerald-400 bg-emerald-500/10 px-3 py-1 rounded-full border border-emerald-500/20">
                Modules
              </span>
              {data && (
                <span className="text-xs text-muted-foreground">
                  {data.topics.length} topic{data.topics.length !== 1 ? "s" : ""} • {totalChunks} chunks
                </span>
              )}
            </div>

            <h1 className="text-4xl md:text-5xl font-bold text-foreground mb-3">
              {data ? formatTitle(data.title) : loading ? "Loading..." : "Modules"}
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl">
              {data
                ? "Explore topic-level modules extracted from this book. Click on any module to start a focused tutoring session."
                : "Loading topic extraction results..."}
            </p>
          </div>
        </div>

        <div className="px-6 md:px-12 py-8 space-y-8">
          {/* Loading */}
          {loading && (
            <div className="flex flex-col items-center justify-center py-20">
              <Loader2 className="w-10 h-10 text-emerald-400 animate-spin mb-4" />
              <p className="text-muted-foreground">Extracting topics from the book...</p>
              <p className="text-xs text-muted-foreground mt-1">This may take a moment on first load</p>
            </div>
          )}

          {/* Error */}
          {!loading && error && (
            <div className="flex flex-col items-center justify-center py-20">
              <AlertCircle className="w-10 h-10 text-red-400/50 mb-4" />
              <p className="text-muted-foreground mb-4">{error}</p>
              <button
                onClick={() => navigate("/community")}
                className="bg-primary/10 text-primary border border-primary/20 px-4 py-2 rounded-xl text-sm font-medium hover:bg-primary hover:text-primary-foreground transition-all"
              >
                Back to Community
              </button>
            </div>
          )}

          {/* Topics Grid */}
          {!loading && !error && data && (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
              {data.topics.map((topic, idx) => {
                const color = topicColors[idx % topicColors.length];
                return (
                  <motion.div
                    key={topic.topic_id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="group relative bg-card border border-border hover:border-emerald-500/30 rounded-2xl overflow-hidden transition-all hover:shadow-xl hover:shadow-black/10"
                  >
                    <div className="p-6">
                      {/* Topic header */}
                      <div className="flex items-start gap-4 mb-4">
                        <div className={cn("w-11 h-11 rounded-xl flex items-center justify-center shrink-0 border", color.bg, color.border)}>
                          <BookOpen className={cn("w-5 h-5", color.text)} />
                        </div>
                        <div className="min-w-0">
                          <h3 className="font-bold text-foreground text-lg leading-tight">{topic.name}</h3>
                          <p className="text-xs text-muted-foreground mt-0.5">Module {topic.topic_id + 1}</p>
                        </div>
                      </div>

                      {/* Chunk count */}
                      <div className="flex items-center gap-4 text-xs text-muted-foreground mb-5 border-t border-border/50 pt-4">
                        <span className="flex items-center gap-1">
                          <Hash className="w-3 h-3 text-emerald-400" />
                          {topic.chunk_count} knowledge chunks
                        </span>
                        <span className="flex items-center gap-1">
                          <Layers className="w-3 h-3" />
                          {Math.round((topic.chunk_count / totalChunks) * 100)}% of book
                        </span>
                      </div>

                      {/* Study button */}
                      <button
                        onClick={() => handleAskAboutTopic(topic.name)}
                        className={cn(
                          "w-full flex items-center justify-center gap-2 font-semibold text-sm py-2.5 rounded-xl border transition-all group/btn",
                          color.bg, color.border, color.text, color.hover,
                        )}
                      >
                        <MessageSquare className="w-4 h-4" />
                        Study This Topic
                        <ChevronRight className="w-4 h-4 opacity-0 -translate-x-1 group-hover/btn:opacity-100 group-hover/btn:translate-x-0 transition-all" />
                      </button>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}

          {/* Empty state */}
          {!loading && !error && data && data.topics.length === 0 && (
            <div className="text-center py-20">
              <Layers className="w-12 h-12 text-muted-foreground/30 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-foreground mb-2">No Topics Found</h3>
              <p className="text-muted-foreground max-w-md mx-auto">
                Topic extraction didn't find any distinct modules for this book.
              </p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}

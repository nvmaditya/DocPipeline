import { useState } from "react";
import { Layout } from "@/components/Layout";
import { useSearchDocuments } from "@workspace/api-client-react";
import { Search as SearchIcon, ArrowRight, Loader2, FileText } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

export default function Search() {
  const [query, setQuery] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

  const { mutate: search, data, isPending } = useSearchDocuments();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    
    setHasSearched(true);
    search({ data: { query, limit: 10 } });
  };

  const results = data?.results || [];

  return (
    <Layout>
      <div className={cn(
        "flex-1 flex flex-col transition-all duration-500 p-6 md:p-12",
        !hasSearched ? "justify-center items-center" : "justify-start"
      )}>
        
        <motion.div 
          layout
          className={cn(
            "w-full max-w-3xl",
            !hasSearched && "text-center mb-10"
          )}
        >
          {!hasSearched && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mb-8">
              <div className="w-20 h-20 rounded-2xl bg-primary/10 text-primary flex items-center justify-center mx-auto mb-6">
                <SearchIcon className="w-10 h-10" />
              </div>
              <h1 className="text-4xl md:text-5xl font-display font-extrabold mb-4">Semantic Search</h1>
              <p className="text-lg text-muted-foreground max-w-xl mx-auto">
                Search across all your documents by meaning, not just exact keywords.
              </p>
            </motion.div>
          )}

          <form onSubmit={handleSearch} className="relative group w-full">
            <div className="absolute inset-0 bg-primary/20 rounded-2xl blur-xl group-hover:bg-primary/30 transition-all opacity-50"></div>
            <div className="relative flex items-center bg-card border-2 border-border focus-within:border-primary/50 rounded-2xl overflow-hidden shadow-xl">
              <div className="pl-6 text-muted-foreground">
                <SearchIcon className="w-6 h-6" />
              </div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="What are you looking for?"
                className="flex-1 bg-transparent border-none py-5 px-4 text-lg focus:outline-none text-foreground placeholder:text-muted-foreground"
              />
              <button 
                type="submit" 
                disabled={!query.trim() || isPending}
                className="mx-2 p-3 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-50"
              >
                {isPending ? <Loader2 className="w-6 h-6 animate-spin" /> : <ArrowRight className="w-6 h-6" />}
              </button>
            </div>
          </form>
        </motion.div>

        <AnimatePresence>
          {hasSearched && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="w-full max-w-4xl mx-auto mt-12 space-y-6"
            >
              <div className="flex items-center justify-between pb-4 border-b border-border/50">
                <h3 className="text-xl font-bold font-display">
                  {isPending ? "Searching..." : `${data?.total || 0} Results for "${data?.query || query}"`}
                </h3>
              </div>

              {isPending ? (
                <div className="space-y-4">
                  {[1, 2, 3].map(i => (
                    <div key={i} className="bg-card border border-border p-6 rounded-2xl animate-pulse">
                      <div className="flex gap-4">
                        <div className="w-10 h-10 bg-white/5 rounded-lg shrink-0" />
                        <div className="flex-1 space-y-3">
                          <div className="h-5 bg-white/5 rounded w-1/3" />
                          <div className="h-4 bg-white/5 rounded w-full" />
                          <div className="h-4 bg-white/5 rounded w-5/6" />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : results.length === 0 ? (
                <div className="text-center py-20">
                  <p className="text-muted-foreground text-lg">No semantic matches found for your query.</p>
                  <p className="text-sm text-muted-foreground/60 mt-2">Try rephrasing or uploading more relevant documents.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {results.map((result, idx) => (
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: idx * 0.05 }}
                      key={`${result.documentId}-${idx}`} 
                      className="bg-card border border-border hover:border-primary/30 p-6 rounded-2xl transition-colors group"
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-3 text-primary">
                          <FileText className="w-5 h-5" />
                          <span className="font-semibold truncate max-w-[250px] md:max-w-md">{result.documentName}</span>
                        </div>
                        <span className="bg-primary/10 text-primary text-xs font-bold px-2.5 py-1 rounded-full border border-primary/20">
                          {(result.score * 100).toFixed(0)}% Match
                        </span>
                      </div>
                      
                      <div className="relative">
                        <div className="absolute left-0 top-0 bottom-0 w-1 bg-primary/20 rounded-full"></div>
                        <p className="pl-4 text-muted-foreground leading-relaxed italic">
                          "...{result.content}..."
                        </p>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </motion.div>
          )}
        </AnimatePresence>

      </div>
    </Layout>
  );
}

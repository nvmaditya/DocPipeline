import { Link } from "wouter";
import { Layout } from "@/components/Layout";
import { useListDocuments } from "@workspace/api-client-react";
import { Search, Plus, FileText, Activity, Database, Users, LogIn, BrainCircuit } from "lucide-react";
import { formatBytes } from "@/lib/utils";
import { motion } from "framer-motion";
import { format } from "date-fns";
import { cn } from "@/lib/utils";
import { useAuth } from "@/context/AuthContext";

export default function Dashboard() {
  const { data: docData, isLoading } = useListDocuments();
  const { user, openAuthModal } = useAuth();

  const documents = docData?.documents || [];
  const totalDocs = docData?.total || 0;

  const readyDocs = documents.filter(d => d.status === 'ready').length;
  const processingDocs = documents.filter(d => d.status === 'processing' || d.status === 'pending').length;
  const totalSize = documents.reduce((acc, curr) => acc + curr.fileSize, 0);

  return (
    <Layout>
      <div className="flex-1 overflow-y-auto">
        <div className="relative w-full h-[280px] md:h-[320px] overflow-hidden">
          <img
            src={`${import.meta.env.BASE_URL}images/dashboard-hero.png`}
            alt="Dashboard Hero"
            className="absolute inset-0 w-full h-full object-cover opacity-40 mix-blend-screen"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-background to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-r from-background via-background/80 to-transparent" />

          <div className="relative h-full flex flex-col justify-end px-6 md:px-12 pb-10">
            <motion.h1
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5 }}
              className="text-4xl md:text-5xl lg:text-6xl font-display font-extrabold text-white max-w-2xl leading-tight"
            >
              Your Knowledge, <span className="text-primary">Intelligence Ready.</span>
            </motion.h1>
            <motion.p
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="text-muted-foreground mt-4 text-lg md:text-xl max-w-xl"
            >
              Upload your documents and let VectorLearn extract the insights. Search by meaning, ask complex questions.
            </motion.p>
          </div>
        </div>

        <div className="px-6 md:px-12 py-8 space-y-8">

          {/* Sign in banner for guests */}
          {!user && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-gradient-to-r from-primary/10 to-blue-500/10 border border-primary/20 rounded-2xl p-5 flex items-center justify-between gap-4"
            >
              <div>
                <p className="font-semibold text-foreground">Sign in to save your work</p>
                <p className="text-sm text-muted-foreground">Create an account to keep your documents and searches across sessions.</p>
              </div>
              <div className="flex gap-3 shrink-0">
                <button
                  onClick={() => openAuthModal("signup")}
                  className="bg-primary text-primary-foreground text-sm font-semibold px-4 py-2 rounded-xl hover:bg-primary/90 transition-colors"
                >
                  Get Started
                </button>
                <button
                  onClick={() => openAuthModal("signin")}
                  className="flex items-center gap-1.5 text-sm font-semibold text-muted-foreground hover:text-foreground border border-border rounded-xl px-4 py-2 transition-colors"
                >
                  <LogIn className="w-4 h-4" />
                  Sign In
                </button>
              </div>
            </motion.div>
          )}

          {/* Quick Actions */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <Link
              href="/documents"
              className="bg-gradient-to-r from-primary to-blue-600 p-[1px] rounded-2xl group hover:-translate-y-1 transition-transform"
            >
              <div className="bg-card/40 backdrop-blur-xl rounded-2xl p-6 h-full flex items-center gap-4 border border-white/10 group-hover:bg-card/20 transition-colors">
                <div className="w-12 h-12 rounded-full bg-white/10 flex items-center justify-center text-white">
                  <Plus className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Upload Document</h3>
                  <p className="text-white/70 text-sm">Add files to your knowledge base</p>
                </div>
              </div>
            </Link>

            <Link
              href="/ask"
              className="bg-card border border-border p-6 rounded-2xl group hover:border-primary/50 hover:-translate-y-1 transition-all"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center text-primary group-hover:scale-110 transition-transform">
                  <Search className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-foreground group-hover:text-primary transition-colors">Ask a Question</h3>
                  <p className="text-muted-foreground text-sm">Query your documents instantly</p>
                </div>
              </div>
            </Link>

            <Link
              href="/community"
              className="bg-card border border-border p-6 rounded-2xl group hover:border-primary/50 hover:-translate-y-1 transition-all"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-emerald-500/10 flex items-center justify-center text-emerald-500 group-hover:scale-110 transition-transform">
                  <Users className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-foreground group-hover:text-primary transition-colors">Community</h3>
                  <p className="text-muted-foreground text-sm">Browse subject knowledge bases</p>
                </div>
              </div>
            </Link>

            <Link
              href="/create-module"
              className="bg-card border border-border p-6 rounded-2xl group hover:border-primary/50 hover:-translate-y-1 transition-all w-full flex-1"
            >
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-indigo-500/10 flex items-center justify-center text-indigo-500 group-hover:scale-110 transition-transform">
                  <BrainCircuit className="w-6 h-6" />
                </div>
                <div>
                  <h3 className="text-lg font-bold text-foreground group-hover:text-primary transition-colors">Create Module</h3>
                  <p className="text-muted-foreground text-sm">Generate your own knowledge base</p>
                </div>
              </div>
            </Link>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-card border border-border rounded-2xl p-6 flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-blue-500/10 text-blue-500 flex items-center justify-center">
                <FileText className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Documents</p>
                <h4 className="text-2xl font-bold text-foreground">
                  {isLoading ? "-" : totalDocs}
                </h4>
              </div>
            </div>
            <div className="bg-card border border-border rounded-2xl p-6 flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-500 flex items-center justify-center">
                <Database className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Storage Used</p>
                <h4 className="text-2xl font-bold text-foreground">
                  {isLoading ? "-" : formatBytes(totalSize)}
                </h4>
              </div>
            </div>
            <div className="bg-card border border-border rounded-2xl p-6 flex items-center gap-4">
              <div className="w-12 h-12 rounded-xl bg-amber-500/10 text-amber-500 flex items-center justify-center">
                <Activity className="w-6 h-6" />
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Status</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-sm font-bold text-emerald-400">{readyDocs} Ready</span>
                  {processingDocs > 0 && (
                    <span className="text-sm font-bold text-amber-400"> • {processingDocs} Processing</span>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Recent Documents */}
          <div>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-display font-bold">Recent Documents</h2>
              <Link href="/documents" className="text-sm font-medium text-primary hover:underline">View All</Link>
            </div>

            {isLoading ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {[1, 2, 3].map(i => (
                  <div key={i} className="bg-card/50 border border-border rounded-xl p-5 h-[120px] animate-pulse" />
                ))}
              </div>
            ) : documents.length === 0 ? (
              <div className="text-center py-12 bg-card border border-border border-dashed rounded-2xl">
                <FileText className="w-12 h-12 text-muted-foreground/50 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-1">No documents yet</h3>
                <p className="text-muted-foreground">Upload your first document to get started.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {documents.slice(0, 6).map((doc) => (
                  <Link key={doc.id} href="/documents" className="block">
                    <div className="bg-card border border-border hover:border-primary/50 hover:shadow-lg rounded-xl p-5 transition-all group cursor-pointer h-full">
                      <div className="flex items-start justify-between mb-4">
                        <div className="w-10 h-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center group-hover:scale-110 transition-transform">
                          <FileText className="w-5 h-5" />
                        </div>
                        <span className={cn(
                          "text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-full",
                          doc.status === 'ready' ? "bg-emerald-500/10 text-emerald-500" :
                          doc.status === 'processing' ? "bg-amber-500/10 text-amber-500" :
                          doc.status === 'error' ? "bg-red-500/10 text-red-500" :
                          "bg-blue-500/10 text-blue-500"
                        )}>
                          {doc.status}
                        </span>
                      </div>
                      <h4 className="font-semibold text-foreground truncate mb-1" title={doc.name}>
                        {doc.name}
                      </h4>
                      <div className="flex items-center justify-between text-xs text-muted-foreground">
                        <span>{formatBytes(doc.fileSize)}</span>
                        <span>{format(new Date(doc.createdAt), 'MMM d, yyyy')}</span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}

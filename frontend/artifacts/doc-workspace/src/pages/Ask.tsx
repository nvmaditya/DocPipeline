import { useState } from "react";
import { useRef, useEffect } from "react";
import { Layout } from "@/components/Layout";
import { useAskQuestion, useListDocuments } from "@workspace/api-client-react";
import { Send, Bot, User, Loader2, Sparkles, FileText, Upload, Users, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { motion } from "framer-motion";
import type { AskSource } from "@workspace/api-client-react";
import { useChatContext } from "@/context/ChatContext";
import { Link } from "wouter";

type Message = {
  id: string;
  role: "user" | "bot";
  content: string;
  sources?: AskSource[];
};

export default function Ask() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);

  const endOfMessagesRef = useRef<HTMLDivElement>(null);
  const { openedFromCommunity, communityPlugin, communityDatabaseId, clearCommunityContext } = useChatContext();
  const { data: docData, isLoading: docsLoading } = useListDocuments();

  const hasDocuments = (docData?.total ?? 0) > 0;
  const canChat = hasDocuments || openedFromCommunity;

  const scrollToBottom = () => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Set up the welcome message based on context
  useEffect(() => {
    if (!docsLoading && canChat && messages.length === 0) {
      const welcomeContent = openedFromCommunity
        ? `Hello! I'm your VectorLearn assistant, connected to the **${communityPlugin}** knowledge base. Ask me anything about this subject and I'll find answers from the indexed content!`
        : `Hello! I'm your VectorLearn assistant. I can see you have ${docData?.total} document${(docData?.total ?? 0) > 1 ? "s" : ""} loaded. Ask me anything about them!`;

      setMessages([{ id: "welcome", role: "bot", content: welcomeContent }]);
    }
  }, [docsLoading, canChat]);

  const { mutate: ask, isPending } = useAskQuestion({
    mutation: {
      onSuccess: (data) => {
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: "bot",
          content: data.answer,
          sources: data.sources
        }]);
      },
      onError: () => {
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          role: "bot",
          content: "I'm sorry, I encountered an error while analyzing the documents. Please try again.",
        }]);
      }
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isPending) return;

    const userMessage = input.trim();
    setInput("");

    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      role: "user",
      content: userMessage
    }]);

    ask({
      data: {
        question: userMessage,
        ...(communityDatabaseId ? { databaseId: communityDatabaseId } : {}),
      },
    });
  };

  // Gate: show a landing screen if user has no docs and didn't come from community
  if (!docsLoading && !canChat) {
    return (
      <Layout>
        <div className="flex-1 flex items-center justify-center p-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-lg w-full text-center"
          >
            <div className="w-20 h-20 rounded-3xl bg-primary/10 border border-primary/20 flex items-center justify-center mx-auto mb-6">
              <Sparkles className="w-10 h-10 text-primary" />
            </div>
            <h1 className="text-3xl font-bold text-foreground mb-3">Start a Conversation</h1>
            <p className="text-muted-foreground mb-8 leading-relaxed">
              To use the AI tutor, you need to either upload your own documents or start a session from a Community knowledge base.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Link href="/documents" className="block">
                <div className="bg-card border border-border hover:border-primary/40 rounded-2xl p-6 text-left transition-all hover:-translate-y-1 hover:shadow-lg group cursor-pointer">
                  <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <Upload className="w-5 h-5" />
                  </div>
                  <h3 className="font-bold text-foreground mb-1">Upload Documents</h3>
                  <p className="text-sm text-muted-foreground mb-3">Add your PDFs, notes, or any text files to your knowledge base.</p>
                  <span className="flex items-center gap-1 text-sm text-primary font-medium">
                    Go to Documents <ChevronRight className="w-4 h-4" />
                  </span>
                </div>
              </Link>

              <Link href="/community" className="block">
                <div className="bg-card border border-border hover:border-primary/40 rounded-2xl p-6 text-left transition-all hover:-translate-y-1 hover:shadow-lg group cursor-pointer">
                  <div className="w-10 h-10 rounded-xl bg-primary/10 text-primary flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                    <Users className="w-5 h-5" />
                  </div>
                  <h3 className="font-bold text-foreground mb-1">Community Knowledge Bases</h3>
                  <p className="text-sm text-muted-foreground mb-3">Start a tutoring session from one of our indexed book databases.</p>
                  <span className="flex items-center gap-1 text-sm text-primary font-medium">
                    Browse Knowledge Bases <ChevronRight className="w-4 h-4" />
                  </span>
                </div>
              </Link>
            </div>
          </motion.div>
        </div>
      </Layout>
    );
  }

  if (docsLoading) {
    return (
      <Layout>
        <div className="flex-1 flex items-center justify-center">
          <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="flex-1 flex flex-col h-[calc(100vh-64px)] md:h-screen max-w-5xl mx-auto w-full relative bg-background">

        {/* Header */}
        <div className="p-6 border-b border-border/50 flex items-center justify-between bg-background/95 backdrop-blur z-10 sticky top-0">
          <div>
            <h1 className="text-2xl font-display font-bold flex items-center gap-2">
              Ask VectorLearn <Sparkles className="w-5 h-5 text-primary" />
            </h1>
            <p className="text-sm text-muted-foreground">
              {openedFromCommunity
                ? `Tutoring session — ${communityPlugin}`
                : "Grounded Q&A over your personal knowledge base"}
            </p>
          </div>
          {openedFromCommunity && (
            <button
              onClick={() => { clearCommunityContext(); setMessages([]); }}
              className="text-xs text-muted-foreground hover:text-foreground border border-border/50 rounded-lg px-3 py-1.5 transition-colors"
            >
              Clear context
            </button>
          )}
        </div>

        {/* Plugin badge */}
        {openedFromCommunity && communityPlugin && (
          <div className="px-6 py-2 bg-primary/5 border-b border-primary/10 flex items-center gap-2">
            <span className="text-xs font-semibold text-primary uppercase tracking-wider">Knowledge Base:</span>
            <span className="text-xs bg-primary/10 text-primary px-2 py-0.5 rounded-full border border-primary/20 font-medium">{communityPlugin}</span>
          </div>
        )}

        {/* Chat Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8 scroll-smooth">
          {messages.map((msg) => (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              key={msg.id}
              className={cn(
                "flex gap-4 max-w-3xl",
                msg.role === "user" ? "ml-auto flex-row-reverse" : ""
              )}
            >
              <div className={cn(
                "w-10 h-10 rounded-full flex items-center justify-center shrink-0 shadow-lg",
                msg.role === "user" ? "bg-primary text-white" : "bg-card border border-border text-primary"
              )}>
                {msg.role === "user" ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
              </div>

              <div className={cn("flex flex-col gap-2", msg.role === "user" ? "items-end" : "items-start")}>
                <div className={cn(
                  "px-6 py-4 rounded-2xl max-w-full leading-relaxed shadow-md",
                  msg.role === "user"
                    ? "bg-primary text-primary-foreground rounded-tr-sm"
                    : "bg-card border border-border rounded-tl-sm text-foreground"
                )}>
                  {msg.content}
                </div>

                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-2 space-y-2 w-full">
                    <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider pl-1">Sources</p>
                    <div className="flex flex-wrap gap-2">
                      {msg.sources.map((source, i) => (
                        <div
                          key={i}
                          className="flex items-center gap-2 bg-secondary/50 border border-border/50 px-3 py-1.5 rounded-lg text-xs hover:border-primary/30 transition-colors cursor-help group relative"
                        >
                          <FileText className="w-3 h-3 text-primary" />
                          <span className="font-medium text-muted-foreground group-hover:text-foreground transition-colors truncate max-w-[150px]">
                            {source.documentName}
                          </span>
                          <div className="absolute bottom-full left-0 mb-2 w-64 p-3 bg-popover border border-popover-border rounded-xl shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-50 pointer-events-none">
                            <p className="text-foreground italic">"{source.content}"</p>
                            <p className="text-primary font-bold mt-2 border-t border-border pt-2">{(source.score * 100).toFixed(0)}% Match</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </motion.div>
          ))}

          {isPending && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-4 max-w-3xl">
              <div className="w-10 h-10 rounded-full bg-card border border-border text-primary flex items-center justify-center shrink-0">
                <Bot className="w-5 h-5" />
              </div>
              <div className="bg-card border border-border px-6 py-4 rounded-2xl rounded-tl-sm flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-primary/50 animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 rounded-full bg-primary/50 animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 rounded-full bg-primary/50 animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </motion.div>
          )}
          <div ref={endOfMessagesRef} className="h-4" />
        </div>

        {/* Input Area */}
        <div className="p-4 md:p-6 bg-background/80 backdrop-blur border-t border-border/50 sticky bottom-0">
          <form
            onSubmit={handleSubmit}
            className="relative flex items-center max-w-4xl mx-auto bg-card border-2 border-border focus-within:border-primary/50 rounded-2xl shadow-xl overflow-hidden transition-all"
          >
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={openedFromCommunity ? `Ask about ${communityPlugin}...` : "Ask a question about your documents..."}
              className="flex-1 bg-transparent border-none py-4 px-6 focus:outline-none text-foreground placeholder:text-muted-foreground"
              disabled={isPending}
            />
            <button
              type="submit"
              disabled={!input.trim() || isPending}
              className="mx-2 p-2.5 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center shrink-0"
            >
              {isPending ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
            </button>
          </form>
          <p className="text-center text-xs text-muted-foreground mt-3">
            VectorLearn uses semantic search to find answers. It may make mistakes.
          </p>
        </div>
      </div>
    </Layout>
  );
}

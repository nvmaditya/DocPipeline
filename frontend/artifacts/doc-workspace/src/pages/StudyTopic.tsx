import React, { useState, useEffect, useRef } from "react";
import { Layout } from "@/components/Layout";
import { useRoute, useLocation } from "wouter";
import { motion } from "framer-motion";
import { useAuth } from "@/context/AuthContext";
import { useAskQuestion } from "@workspace/api-client-react";
import type { AskSource } from "@workspace/api-client-react";
import {
  ArrowLeft,
  Loader2,
  AlertCircle,
  CheckCircle2,
  XCircle,
  MessageSquare,
  Send,
  Bot,
  User,
  X,
  GraduationCap,
  FileText,
} from "lucide-react";
import { cn } from "@/lib/utils";

type QuizQuestion = {
  question: string;
  options: string[];
  correct_answer: number;
};

type StudyData = {
  study_content: string;
  quiz: QuizQuestion[];
};

type ChatMessage = {
  id: string;
  role: "user" | "bot";
  content: string;
  sources?: AskSource[];
};

function formatTitle(title: string): string {
  return title
    .replace(/([a-z])([A-Z])/g, "$1 $2")
    .replace(/[-_]+/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}

/** Very light markdown-ish renderer for study content. */
function renderStudyContent(content: string) {
  const lines = content.split("\n");
  const elements: React.ReactElement[] = [];
  let listBuffer: string[] = [];
  let listType: "ul" | "ol" | null = null;

  const flushList = () => {
    if (listBuffer.length === 0) return;
    const Tag = listType === "ol" ? "ol" : "ul";
    elements.push(
      <Tag
        key={`list-${elements.length}`}
        className={cn(
          "my-3 space-y-1.5 text-muted-foreground",
          listType === "ol" ? "list-decimal pl-6" : "list-disc pl-6"
        )}
      >
        {listBuffer.map((item, i) => (
          <li key={i} className="leading-relaxed">{renderInline(item)}</li>
        ))}
      </Tag>
    );
    listBuffer = [];
    listType = null;
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Headings
    if (line.startsWith("### ")) {
      flushList();
      elements.push(
        <h3 key={`h3-${i}`} className="text-lg font-bold text-foreground mt-8 mb-3 flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-primary" />
          {renderInline(line.slice(4))}
        </h3>
      );
      continue;
    }
    if (line.startsWith("## ")) {
      flushList();
      elements.push(
        <h2 key={`h2-${i}`} className="text-xl font-bold text-foreground mt-10 mb-4 pb-2 border-b border-border/50">
          {renderInline(line.slice(3))}
        </h2>
      );
      continue;
    }

    // Unordered list
    const ulMatch = line.match(/^[-*]\s+(.*)/);
    if (ulMatch) {
      if (listType === "ol") flushList();
      listType = "ul";
      listBuffer.push(ulMatch[1]);
      continue;
    }

    // Ordered list
    const olMatch = line.match(/^\d+\.\s+(.*)/);
    if (olMatch) {
      if (listType === "ul") flushList();
      listType = "ol";
      listBuffer.push(olMatch[1]);
      continue;
    }

    flushList();

    // Empty line
    if (line.trim() === "") continue;

    // Regular paragraph
    elements.push(
      <p key={`p-${i}`} className="text-muted-foreground leading-relaxed mb-4">
        {renderInline(line)}
      </p>
    );
  }

  flushList();
  return elements;
}

/** Render bold and inline code within text. */
function renderInline(text: string): (string | React.ReactElement)[] {
  const parts: (string | React.ReactElement)[] = [];
  const regex = /(\*\*(.+?)\*\*|`(.+?)`)/g;
  let lastIndex = 0;
  let match: RegExpExecArray | null;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.slice(lastIndex, match.index));
    }
    if (match[2]) {
      parts.push(<strong key={`b-${match.index}`} className="text-foreground font-semibold">{match[2]}</strong>);
    } else if (match[3]) {
      parts.push(
        <code key={`c-${match.index}`} className="bg-primary/10 text-primary px-1.5 py-0.5 rounded text-[0.85em] font-mono">
          {match[3]}
        </code>
      );
    }
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    parts.push(text.slice(lastIndex));
  }

  return parts.length > 0 ? parts : [text];
}

export default function StudyTopic() {
  const [, params] = useRoute("/study/:databaseId/:topicName");
  const databaseId = params?.databaseId ?? "";
  const topicName = decodeURIComponent(params?.topicName ?? "");
  const [, navigate] = useLocation();
  const { user, token, openAuthModal } = useAuth();

  // Study data state
  const [studyData, setStudyData] = useState<StudyData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Quiz state
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, number>>({});
  const [quizSubmitted, setQuizSubmitted] = useState(false);

  // Chat sidebar state
  const [chatOpen, setChatOpen] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Fetch study content
  useEffect(() => {
    if (!databaseId || !topicName || !user) return;
    setLoading(true);
    setError(null);

    fetch("/api/study/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: JSON.stringify({
        database_id: databaseId,
        topic_name: topicName,
      }),
    })
      .then(async (res) => {
        if (!res.ok) {
          if (res.status === 401) throw new Error("Sign in to access study materials.");
          throw new Error("Failed to generate study content.");
        }
        return res.json();
      })
      .then((d: StudyData) => setStudyData(d))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [databaseId, topicName, user]);

  // Chat welcome message
  useEffect(() => {
    if (chatOpen && chatMessages.length === 0) {
      setChatMessages([
        {
          id: "welcome",
          role: "bot",
          content: `Hi! I'm here to help you with **${topicName}**. Ask me anything about this topic!`,
        },
      ]);
    }
  }, [chatOpen]);

  // Scroll chat to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  // Ask hook for chat
  const { mutate: askQuestion, isPending: chatPending } = useAskQuestion({
    mutation: {
      onSuccess: (data: any) => {
        setChatMessages((prev) => [
          ...prev,
          { id: Date.now().toString(), role: "bot", content: data.answer, sources: data.sources },
        ]);
      },
      onError: () => {
        setChatMessages((prev) => [
          ...prev,
          { id: Date.now().toString(), role: "bot", content: "Sorry, I encountered an error. Please try again." },
        ]);
      },
    },
  });

  const handleChatSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || chatPending) return;
    const msg = chatInput.trim();
    setChatInput("");
    setChatMessages((prev) => [...prev, { id: Date.now().toString(), role: "user", content: msg }]);
    askQuestion({ data: { question: msg, databaseId } as any });
  };

  // Quiz handlers
  const handleSelectAnswer = (qIdx: number, optIdx: number) => {
    if (quizSubmitted) return;
    setSelectedAnswers((prev) => ({ ...prev, [qIdx]: optIdx }));
  };

  const handleSubmitQuiz = () => {
    setQuizSubmitted(true);
  };

  const quizScore =
    studyData?.quiz.reduce((acc, q, idx) => (selectedAnswers[idx] === q.correct_answer ? acc + 1 : acc), 0) ?? 0;

  const allAnswered = studyData?.quiz.length ? Object.keys(selectedAnswers).length === studyData.quiz.length : false;

  if (!user) {
    return (
      <Layout>
        <div className="flex-1 flex items-center justify-center p-8">
          <div className="text-center">
            <GraduationCap className="w-16 h-16 text-primary/30 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Sign In Required</h2>
            <p className="text-muted-foreground mb-6">You need to sign in to access study materials.</p>
            <button onClick={() => openAuthModal("signin")} className="bg-primary text-primary-foreground px-6 py-3 rounded-xl font-semibold hover:bg-primary/90 transition-colors">
              Sign In
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="flex-1 flex overflow-hidden">
        {/* ─── Main content area ─── */}
        <div className={cn("flex-1 overflow-y-auto transition-all duration-300", chatOpen ? "mr-0" : "")}>
          {/* Hero */}
          <div className="relative border-b border-border/50 bg-gradient-to-b from-violet-500/5 to-background px-6 md:px-12 py-10">
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
              <div className="absolute top-0 left-1/4 w-64 h-64 bg-violet-500/5 rounded-full blur-3xl" />
            </div>
            <div className="relative max-w-4xl">
              <button
                onClick={() => navigate(`/book-modules/${databaseId}`)}
                className="flex items-center gap-1.5 text-sm text-muted-foreground hover:text-foreground mb-6 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to Modules
              </button>

              <div className="flex items-center gap-2 mb-3">
                <span className="text-xs font-bold uppercase tracking-widest text-violet-400 bg-violet-500/10 px-3 py-1 rounded-full border border-violet-500/20">
                  Study Material
                </span>
              </div>

              <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-3">{topicName}</h1>
              <p className="text-muted-foreground">
                Comprehensive study guide generated from the knowledge base. Read through the material, then test yourself with the quiz below.
              </p>
            </div>
          </div>

          <div className="px-6 md:px-12 py-8 max-w-4xl">
            {/* Loading */}
            {loading && (
              <div className="flex flex-col items-center justify-center py-20">
                <Loader2 className="w-10 h-10 text-violet-400 animate-spin mb-4" />
                <p className="text-muted-foreground">Generating study material...</p>
                <p className="text-xs text-muted-foreground mt-1">This may take 10-20 seconds</p>
              </div>
            )}

            {/* Error */}
            {!loading && error && (
              <div className="flex flex-col items-center justify-center py-20">
                <AlertCircle className="w-10 h-10 text-red-400/50 mb-4" />
                <p className="text-muted-foreground mb-4">{error}</p>
                <button
                  onClick={() => navigate(`/book-modules/${databaseId}`)}
                  className="bg-primary/10 text-primary border border-primary/20 px-4 py-2 rounded-xl text-sm font-medium hover:bg-primary hover:text-primary-foreground transition-all"
                >
                  Back to Modules
                </button>
              </div>
            )}

            {/* ─── Study Content ─── */}
            {!loading && !error && studyData && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                {/* Content card */}
                <div className="bg-card border border-border rounded-2xl p-8 md:p-10 mb-10 shadow-lg">
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-10 h-10 rounded-xl bg-violet-500/10 border border-violet-500/20 flex items-center justify-center">
                      <FileText className="w-5 h-5 text-violet-400" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold text-foreground">Study Guide</h2>
                      <p className="text-xs text-muted-foreground">Generated from indexed knowledge base</p>
                    </div>
                  </div>

                  <div className="prose-custom">
                    {renderStudyContent(studyData.study_content)}
                  </div>
                </div>

                {/* ─── Quiz Section ─── */}
                {studyData.quiz.length > 0 && (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="mb-12"
                  >
                    <div className="flex items-center gap-3 mb-6">
                      <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                        <GraduationCap className="w-5 h-5 text-emerald-400" />
                      </div>
                      <div>
                        <h2 className="text-xl font-bold text-foreground">Knowledge Check</h2>
                        <p className="text-xs text-muted-foreground">
                          {studyData.quiz.length} questions • Test your understanding
                        </p>
                      </div>
                    </div>

                    <div className="space-y-6">
                      {studyData.quiz.map((q, qIdx) => {
                        const selected = selectedAnswers[qIdx];
                        const isCorrect = quizSubmitted && selected === q.correct_answer;
                        const isWrong = quizSubmitted && selected !== undefined && selected !== q.correct_answer;

                        return (
                          <motion.div
                            key={qIdx}
                            initial={{ opacity: 0, y: 10 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: 0.05 * qIdx }}
                            className={cn(
                              "bg-card border rounded-2xl p-6 transition-all",
                              quizSubmitted && isCorrect && "border-emerald-500/30 bg-emerald-500/5",
                              quizSubmitted && isWrong && "border-red-500/30 bg-red-500/5",
                              !quizSubmitted && "border-border hover:border-primary/20"
                            )}
                          >
                            <div className="flex items-start gap-3 mb-4">
                              <span className="text-xs font-bold text-muted-foreground bg-secondary px-2.5 py-1 rounded-lg shrink-0">
                                Q{qIdx + 1}
                              </span>
                              <p className="font-semibold text-foreground leading-relaxed">{q.question}</p>
                              {quizSubmitted && (
                                <div className="shrink-0 ml-auto">
                                  {isCorrect ? (
                                    <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                                  ) : (
                                    <XCircle className="w-5 h-5 text-red-400" />
                                  )}
                                </div>
                              )}
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                              {q.options.map((opt, optIdx) => {
                                const isSelected = selected === optIdx;
                                const isCorrectOption = quizSubmitted && optIdx === q.correct_answer;
                                const isWrongSelection = quizSubmitted && isSelected && optIdx !== q.correct_answer;

                                return (
                                  <button
                                    key={optIdx}
                                    onClick={() => handleSelectAnswer(qIdx, optIdx)}
                                    disabled={quizSubmitted}
                                    className={cn(
                                      "flex items-center gap-3 px-4 py-3 rounded-xl border text-left text-sm transition-all",
                                      !quizSubmitted && !isSelected && "border-border hover:border-primary/30 hover:bg-primary/5",
                                      !quizSubmitted && isSelected && "border-primary bg-primary/10 text-primary font-medium",
                                      isCorrectOption && "border-emerald-500/50 bg-emerald-500/10 text-emerald-400 font-medium",
                                      isWrongSelection && "border-red-500/50 bg-red-500/10 text-red-400 line-through",
                                      quizSubmitted && !isCorrectOption && !isWrongSelection && "opacity-50"
                                    )}
                                  >
                                    <span
                                      className={cn(
                                        "w-6 h-6 rounded-full border-2 flex items-center justify-center shrink-0 text-xs font-bold",
                                        !quizSubmitted && !isSelected && "border-border text-muted-foreground",
                                        !quizSubmitted && isSelected && "border-primary bg-primary text-white",
                                        isCorrectOption && "border-emerald-500 bg-emerald-500 text-white",
                                        isWrongSelection && "border-red-500 bg-red-500 text-white"
                                      )}
                                    >
                                      {String.fromCharCode(65 + optIdx)}
                                    </span>
                                    {opt}
                                  </button>
                                );
                              })}
                            </div>
                          </motion.div>
                        );
                      })}
                    </div>

                    {/* Submit / Score */}
                    <div className="mt-8 flex items-center justify-center">
                      {!quizSubmitted ? (
                        <button
                          onClick={handleSubmitQuiz}
                          disabled={!allAnswered}
                          className={cn(
                            "px-8 py-3 rounded-xl font-bold text-base transition-all",
                            allAnswered
                              ? "bg-emerald-500 text-white hover:bg-emerald-400 shadow-lg shadow-emerald-500/25"
                              : "bg-secondary text-muted-foreground cursor-not-allowed"
                          )}
                        >
                          Submit Quiz ({Object.keys(selectedAnswers).length}/{studyData.quiz.length} answered)
                        </button>
                      ) : (
                        <motion.div
                          initial={{ scale: 0.9, opacity: 0 }}
                          animate={{ scale: 1, opacity: 1 }}
                          className="text-center"
                        >
                          <div
                            className={cn(
                              "inline-flex items-center gap-3 px-8 py-4 rounded-2xl font-bold text-lg border",
                              quizScore >= studyData.quiz.length * 0.7
                                ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400"
                                : quizScore >= studyData.quiz.length * 0.4
                                ? "bg-amber-500/10 border-amber-500/30 text-amber-400"
                                : "bg-red-500/10 border-red-500/30 text-red-400"
                            )}
                          >
                            {quizScore >= studyData.quiz.length * 0.7 ? (
                              <CheckCircle2 className="w-6 h-6" />
                            ) : (
                              <AlertCircle className="w-6 h-6" />
                            )}
                            Score: {quizScore} / {studyData.quiz.length}
                            <span className="text-sm font-normal opacity-70">
                              ({Math.round((quizScore / studyData.quiz.length) * 100)}%)
                            </span>
                          </div>
                          <p className="text-muted-foreground text-sm mt-3">
                            {quizScore >= studyData.quiz.length * 0.7
                              ? "Great job! You have a solid understanding of this topic."
                              : "Review the study material and try again to improve your score."}
                          </p>
                          <button
                            onClick={() => {
                              setSelectedAnswers({});
                              setQuizSubmitted(false);
                            }}
                            className="mt-4 text-primary text-sm font-medium hover:underline"
                          >
                            Retry Quiz
                          </button>
                        </motion.div>
                      )}
                    </div>
                  </motion.div>
                )}
              </motion.div>
            )}
          </div>
        </div>

        {/* ─── Chat Toggle Button ─── */}
        {!chatOpen && (
          <motion.button
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            onClick={() => setChatOpen(true)}
            className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full bg-primary text-white shadow-xl shadow-primary/25 flex items-center justify-center hover:bg-primary/90 transition-colors"
          >
            <MessageSquare className="w-6 h-6" />
          </motion.button>
        )}

        {/* ─── Chat Sidebar ─── */}
        {chatOpen && (
          <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="w-[380px] border-l border-border bg-card/95 backdrop-blur-xl flex flex-col h-screen sticky top-0 z-40 shrink-0"
          >
            {/* Chat header */}
            <div className="p-4 border-b border-border/50 flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-primary" />
                </div>
                <div>
                  <p className="text-sm font-bold text-foreground">Study Assistant</p>
                  <p className="text-[10px] text-muted-foreground">{topicName}</p>
                </div>
              </div>
              <button
                onClick={() => setChatOpen(false)}
                className="p-1.5 rounded-lg hover:bg-secondary transition-colors text-muted-foreground hover:text-foreground"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Chat messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {chatMessages.map((msg) => (
                <div
                  key={msg.id}
                  className={cn("flex gap-2", msg.role === "user" ? "flex-row-reverse" : "")}
                >
                  <div
                    className={cn(
                      "w-7 h-7 rounded-full flex items-center justify-center shrink-0",
                      msg.role === "user"
                        ? "bg-primary text-white"
                        : "bg-secondary border border-border text-primary"
                    )}
                  >
                    {msg.role === "user" ? <User className="w-3.5 h-3.5" /> : <Bot className="w-3.5 h-3.5" />}
                  </div>
                  <div
                    className={cn(
                      "px-3.5 py-2.5 rounded-xl text-sm leading-relaxed max-w-[85%]",
                      msg.role === "user"
                        ? "bg-primary text-primary-foreground rounded-tr-sm"
                        : "bg-secondary border border-border rounded-tl-sm text-foreground"
                    )}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}

              {chatPending && (
                <div className="flex gap-2">
                  <div className="w-7 h-7 rounded-full bg-secondary border border-border text-primary flex items-center justify-center shrink-0">
                    <Bot className="w-3.5 h-3.5" />
                  </div>
                  <div className="bg-secondary border border-border px-3.5 py-2.5 rounded-xl rounded-tl-sm flex items-center gap-1.5">
                    <div className="w-1.5 h-1.5 rounded-full bg-primary/50 animate-bounce" style={{ animationDelay: "0ms" }} />
                    <div className="w-1.5 h-1.5 rounded-full bg-primary/50 animate-bounce" style={{ animationDelay: "150ms" }} />
                    <div className="w-1.5 h-1.5 rounded-full bg-primary/50 animate-bounce" style={{ animationDelay: "300ms" }} />
                  </div>
                </div>
              )}
              <div ref={chatEndRef} className="h-2" />
            </div>

            {/* Chat input */}
            <div className="p-3 border-t border-border/50">
              <form onSubmit={handleChatSubmit} className="flex items-center gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  placeholder="Ask about this topic..."
                  className="flex-1 bg-secondary border border-border rounded-xl px-3.5 py-2.5 text-sm focus:outline-none focus:border-primary/50 text-foreground placeholder:text-muted-foreground"
                  disabled={chatPending}
                />
                <button
                  type="submit"
                  disabled={!chatInput.trim() || chatPending}
                  className="p-2.5 bg-primary text-white rounded-xl hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
                >
                  {chatPending ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                </button>
              </form>
            </div>
          </motion.div>
        )}
      </div>
    </Layout>
  );
}

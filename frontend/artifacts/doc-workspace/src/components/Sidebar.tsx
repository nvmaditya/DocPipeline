import { Link, useLocation } from "wouter";
import { cn } from "@/lib/utils";
import {
    BrainCircuit,
    LayoutDashboard,
    Files,
    Search,
    MessageSquare,
    Users,
    LogIn,
    LogOut,
    ChevronDown,
    BookPlus,
} from "lucide-react";
import { motion } from "framer-motion";
import { useAuth } from "@/context/AuthContext";
import { useState } from "react";

const navItems = [
    { href: "/", label: "Dashboard", icon: LayoutDashboard },
    { href: "/documents", label: "Documents", icon: Files },
    { href: "/search", label: "Semantic Search", icon: Search },
    { href: "/ask", label: "Ask VectorLearn", icon: MessageSquare },
    { href: "/community", label: "Community", icon: Users },
    { href: "/create-module", label: "Create Module", icon: BookPlus },
];

export function Sidebar() {
    const [location] = useLocation();
    const { user, openAuthModal, signOut } = useAuth();
    const [userMenuOpen, setUserMenuOpen] = useState(false);

    return (
        <aside className="w-64 border-r border-border bg-card/50 backdrop-blur-xl h-screen sticky top-0 flex flex-col z-40 hidden md:flex">
            <div className="h-16 flex items-center px-6 border-b border-border/50">
                <Link
                    href="/"
                    className="flex items-center gap-3 transition-opacity hover:opacity-80"
                >
                    <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-primary to-blue-400 flex items-center justify-center shadow-lg shadow-primary/25">
                        <BrainCircuit className="w-5 h-5 text-white" />
                    </div>
                    <span className="font-display font-bold text-xl tracking-tight text-foreground">
                        VectorLearn
                    </span>
                </Link>
            </div>

            <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
                {navItems.map((item) => {
                    const isActive = location === item.href;

                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className="block relative"
                        >
                            <div
                                className={cn(
                                    "flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 relative z-10",
                                    isActive
                                        ? "text-foreground"
                                        : "text-muted-foreground hover:text-foreground hover:bg-white/5",
                                )}
                            >
                                <item.icon
                                    className={cn(
                                        "w-5 h-5",
                                        isActive ? "text-foreground" : "",
                                    )}
                                />
                                {item.label}
                                {item.href === "/community" && (
                                    <span className="ml-auto text-[9px] font-bold uppercase tracking-wider bg-primary/20 text-primary px-1.5 py-0.5 rounded-full">
                                        New
                                    </span>
                                )}
                            </div>
                            {isActive && (
                                <motion.div
                                    layoutId="active-nav-bg"
                                    className="absolute inset-0 bg-primary/20 border border-primary/30 rounded-xl z-0"
                                    initial={false}
                                    transition={{
                                        type: "spring",
                                        stiffness: 300,
                                        damping: 30,
                                    }}
                                />
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* User section */}
            <div className="p-4 border-t border-border/50">
                {user ? (
                    <div className="relative">
                        <button
                            onClick={() => setUserMenuOpen(!userMenuOpen)}
                            className="w-full flex items-center gap-3 p-3 rounded-xl hover:bg-white/5 transition-colors"
                        >
                            <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/30 overflow-hidden shrink-0">
                                <img
                                    src={user.avatar}
                                    alt={user.name}
                                    className="w-full h-full object-cover"
                                />
                            </div>
                            <div className="flex-1 text-left min-w-0">
                                <p className="text-sm font-semibold text-foreground truncate">
                                    {user.name}
                                </p>
                                <p className="text-[10px] text-muted-foreground truncate">
                                    {user.email}
                                </p>
                            </div>
                            <ChevronDown
                                className={cn(
                                    "w-4 h-4 text-muted-foreground transition-transform",
                                    userMenuOpen && "rotate-180",
                                )}
                            />
                        </button>

                        {userMenuOpen && (
                            <motion.div
                                initial={{ opacity: 0, y: -8 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="absolute bottom-full left-0 right-0 mb-2 bg-card border border-border rounded-xl shadow-xl overflow-hidden"
                            >
                                <button
                                    onClick={() => {
                                        signOut();
                                        setUserMenuOpen(false);
                                    }}
                                    className="w-full flex items-center gap-2 px-4 py-3 text-sm text-muted-foreground hover:text-destructive hover:bg-destructive/5 transition-colors"
                                >
                                    <LogOut className="w-4 h-4" />
                                    Sign Out
                                </button>
                            </motion.div>
                        )}
                    </div>
                ) : (
                    <button
                        onClick={() => openAuthModal("signin")}
                        className="w-full flex items-center gap-3 p-3 rounded-xl bg-primary/10 border border-primary/20 hover:bg-primary/20 transition-colors text-primary"
                    >
                        <LogIn className="w-5 h-5" />
                        <div className="text-left">
                            <p className="text-sm font-semibold">Sign In</p>
                            <p className="text-[10px] text-primary/70">
                                Access all features
                            </p>
                        </div>
                    </button>
                )}
            </div>
        </aside>
    );
}

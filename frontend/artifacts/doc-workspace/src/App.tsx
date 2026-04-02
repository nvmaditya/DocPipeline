import { Switch, Route, Router as WouterRouter } from "wouter";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/not-found";
import { AuthProvider } from "@/context/AuthContext";
import { ChatProvider } from "@/context/ChatContext";
import { AuthModal } from "@/components/AuthModal";

import Dashboard from "@/pages/Dashboard";
import Documents from "@/pages/Documents";
import Search from "@/pages/Search";
import Ask from "@/pages/Ask";
import Community from "@/pages/Community";
import CreateModule from "@/pages/CreateModule";
import BookModules from "@/pages/BookModules";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      refetchOnWindowFocus: false,
    },
  },
});

function Router() {
  return (
    <Switch>
      <Route path="/" component={Dashboard} />
      <Route path="/documents" component={Documents} />
      <Route path="/search" component={Search} />
      <Route path="/ask" component={Ask} />
      <Route path="/community" component={Community} />
      <Route path="/create-module" component={CreateModule} />
      <Route path="/book-modules/:databaseId" component={BookModules} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ChatProvider>
          <TooltipProvider>
            <div className="dark min-h-screen bg-background text-foreground">
              <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, "")}>
                <Router />
              </WouterRouter>
              <AuthModal />
              <Toaster />
            </div>
          </TooltipProvider>
        </ChatProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;

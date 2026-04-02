import { createContext, useContext, useState, ReactNode } from "react";

type ChatContextType = {
  openedFromCommunity: boolean;
  communityPlugin: string | null;
  communityDatabaseId: string | null;
  openChatFromCommunity: (pluginName: string, databaseId: string) => void;
  clearCommunityContext: () => void;
};

const ChatContext = createContext<ChatContextType | null>(null);

export function ChatProvider({ children }: { children: ReactNode }) {
  const [openedFromCommunity, setOpenedFromCommunity] = useState(false);
  const [communityPlugin, setCommunityPlugin] = useState<string | null>(null);
  const [communityDatabaseId, setCommunityDatabaseId] = useState<string | null>(null);

  const openChatFromCommunity = (pluginName: string, databaseId: string) => {
    setOpenedFromCommunity(true);
    setCommunityPlugin(pluginName);
    setCommunityDatabaseId(databaseId);
  };

  const clearCommunityContext = () => {
    setOpenedFromCommunity(false);
    setCommunityPlugin(null);
    setCommunityDatabaseId(null);
  };

  return (
    <ChatContext.Provider value={{ openedFromCommunity, communityPlugin, communityDatabaseId, openChatFromCommunity, clearCommunityContext }}>
      {children}
    </ChatContext.Provider>
  );
}

export function useChatContext() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error("useChatContext must be used inside ChatProvider");
  return ctx;
}

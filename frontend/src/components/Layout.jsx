import { useState, useEffect, useRef } from "react";
import { Outlet, useNavigate, useLocation } from "react-router-dom";

import Sidebar from "./Sidebar";
import { useAuth } from "../context/AuthContext";

export default function Layout() {
  localStorage.removeItem("chatList");
  localStorage.removeItem("chatMessages");
  localStorage.removeItem("activeChatId");
  const navigate = useNavigate();
  const location = useLocation();
  const { isLoggedIn, token } = useAuth();
  const unloadRef = useRef(false);

  const [chats, setChats] = useState(() => {
    const stored = localStorage.getItem("chatList");
    return stored ? JSON.parse(stored) : [];
  });

  const [activeChatId, setActiveChatId] = useState(() => {
    return localStorage.getItem("activeChatId") || null;
  });

  const [chatMessages, setChatMessages] = useState(() => {
    const stored = localStorage.getItem("chatMessages");
    return stored ? JSON.parse(stored) : {};
  });

  const [chatIdIndexMap, setChatIdIndexMap] = useState({});
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  useEffect(() => {
    localStorage.setItem("chatList", JSON.stringify(chats));
  }, [chats]);

  useEffect(() => {
    localStorage.setItem("activeChatId", activeChatId);
  }, [activeChatId]);

  useEffect(() => {
    localStorage.setItem("chatMessages", JSON.stringify(chatMessages));
  }, [chatMessages]);

  // ✅ Fetch chat history from backend (GET /history with token)
  useEffect(() => {
    const fetchChats = async () => {
      try {
        const res = await fetch("http://localhost:8000/history", {
          method: "GET",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        if (!res.ok) throw new Error("Failed to fetch history");

        let data;
        const initial_data = await res.json();
        if (initial_data.length === 0) {
          data = [[]] 
        }
        else { 
          data= initial_data
        }

        let formattedChats = [];
        let formattedMessages = {};
        let idIndexMap = {};
        for (let i = data.length - 1; i >= 0; i--) { 
          formattedChats.push({
            id: String(i),
            title: `Chat ${i + 1}`,
          })
          formattedMessages[String(i)] = data[i];
          idIndexMap[String(i)] = i;
        }
        
        setChats(formattedChats);
        setChatMessages(formattedMessages);
        setChatIdIndexMap(idIndexMap);

        if (formattedChats.length > 0) setActiveChatId(formattedChats[0].id);
      } catch (err) {
        console.error("Failed to fetch chat history:", err);
      }
    };

    if (isLoggedIn && token) {
      fetchChats();
    }
  }, [isLoggedIn, token]);

  // 🧹 Clear chat history for guests on window close
  useEffect(() => {
    const handleBeforeUnload = (e) => {
      if (!isLoggedIn && !unloadRef.current) {
        unloadRef.current = true;
        localStorage.removeItem("chatList");
        localStorage.removeItem("chatMessages");
        localStorage.removeItem("activeChatId");

        e.preventDefault();
        e.returnValue = "Are you sure you want to leave? Your chats will be lost.";
        return e;
      }
    };

    window.addEventListener("beforeunload", handleBeforeUnload);
    return () => window.removeEventListener("beforeunload", handleBeforeUnload);
  }, [isLoggedIn]);

  const generateUniqueTitle = (idStr) => {
    return `Chat ${parseInt(idStr, 10) + 1}`;
  };

  const handleNewChat = () => {
    const maxId = chats.length > 0 ? Math.max(...chats.map((c) => parseInt(c.id, 10))) : -1;
    const id = String(maxId + 1);
    const newChat = { id, title: generateUniqueTitle(id) };
    const updatedChats = [newChat, ...chats];
    const updatedMessages = { ...chatMessages, [id]: [] };

    setChats(updatedChats);
    setActiveChatId(id);
    setChatMessages(updatedMessages);
    navigate("/chatbot");
    localStorage.setItem("activeChatId", id)
  };

  const handleSelectChat = (id) => {
    setActiveChatId(id);
    localStorage.setItem("activeChatId", id)
    navigate("/chatbot");
  };

  const handleRenameChat = (id, newTitle) => {
    setChats(chats.map((chat) => (chat.id === id ? { ...chat, title: newTitle } : chat)));
  };

  const handleDeleteChat = (id) => {
    const filteredChats = chats.filter((chat) => chat.id !== id);
    const updatedMessages = { ...chatMessages };
    delete updatedMessages[id];

    setChats(filteredChats);
    setChatMessages(updatedMessages);

    if (filteredChats.length > 0) {
      setActiveChatId(filteredChats[0].id);
      localStorage.setItem("activeChatId", filteredChats[0].id);
    } else {
      const maxId = chats.length > 0 ? Math.max(...chats.map((c) => parseInt(c.id, 10))) : -1;
      const newId = String(maxId + 1);
      localStorage.setItem("activeChatId", newId)
      const newChat = { id: newId, title: generateUniqueTitle(newId) };
      setChats([newChat]);
      setActiveChatId(newId);
      setChatMessages({ [newId]: [] });
    }
  };

  const handleFirstUserMessage = (messageText) => {
    const maxId = chats.length > 0 ? Math.max(...chats.map((c) => parseInt(c.id, 10))) : -1;
    const id = String(maxId + 1);
    const newChat = { id, title: generateUniqueTitle(id) };
    const newMessages = [{ role: "user", content: messageText }];
    const updatedChats = [newChat, ...chats];

    setChats(updatedChats);
    setActiveChatId(id);
    localStorage.setItem("activeChatId", id)
    setChatMessages((prev) => ({ ...prev, [id]: newMessages }));
    return id;
  };

  useEffect(() => {
    if (location.state?.createNewChat) {
      handleNewChat();
      navigate("/chatbot", { replace: true, state: {} });
    }
  }, [location]);

  return (
    <div className="flex min-h-screen">
      {!sidebarCollapsed ? (
        <Sidebar
          chats={chats}
          activeChatId={activeChatId}
          onNewChat={handleNewChat}
          onSelectChat={handleSelectChat}
          onRenameChat={handleRenameChat}
          onDeleteChat={handleDeleteChat}
          onToggleCollapse={() => setSidebarCollapsed(true)}
        />
      ) : (
        <div className="w-10 bg-[#1b0d3a] text-white flex items-center justify-center">
          <button
            onClick={() => setSidebarCollapsed(false)}
            className="text-white hover:text-purple-400"
            title="Expand Sidebar"
          >
            &gt;&gt;
          </button>
        </div>
      )}
      <div className="flex-grow">
        <Outlet
          context={{
            chats,
            chatMessages,
            activeChatId,
            setActiveChatId,
            setChatMessages,
            handleFirstUserMessage,
            handleNewChat,
            chatIdIndexMap,
          }}
        />
      </div>
    </div>
  );
}

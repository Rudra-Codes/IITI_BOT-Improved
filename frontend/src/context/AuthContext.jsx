import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);
  const [userEmail, setUserEmail] = useState(null);
  const [userName, setUserName] = useState("");
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Load from localStorage on first mount
  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedEmail = localStorage.getItem("userEmail");

    if (storedToken) {
      setToken(storedToken);
      setIsLoggedIn(true);
    }

    if (storedEmail) {
      setUserEmail(storedEmail);
      setUserName(storedEmail.split("@")[0]);
    }
  }, []);

  const updateToken = (newToken) => {
    setToken(newToken);
    localStorage.setItem("token", newToken);
    setIsLoggedIn(true);
  };

  const setUserId = (email) => {
    setUserEmail(email);
    localStorage.setItem("userEmail", email);
    setUserName(email.split("@")[0]);
  };

  const logout = async () => {
    setToken(null);
    setUserEmail(null);
    setUserName("");
    setIsLoggedIn(false);
    localStorage.clear();
    sessionStorage.clear();
    if ('caches' in window) {
      try {
        const cacheNames = await caches.keys();
        await Promise.all(cacheNames.map(name => caches.delete(name)));
      } catch (e) {
        console.error("Failed to clear caches:", e);
      }
    }
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        setToken: updateToken,
        userEmail,
        userName,
        isLoggedIn,
        setIsLoggedIn,
        setUserId,
        setUserName,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);

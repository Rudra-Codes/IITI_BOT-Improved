import React, { Suspense, lazy } from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";

import App from "./App";
import Layout from "./components/Layout";
import { AuthProvider } from "./context/AuthContext";

import "./index.css";

// Lazy loaded pages to optimize routing
const HomePage = lazy(() => import("./pages/HomePage"));
const ChatbotPage = lazy(() => import("./pages/ChatbotPage"));
const LoginPage = lazy(() => import("./pages/LoginPage"));
const SignupPage = lazy(() => import("./pages/SignupPage"));
const About = lazy(() => import("./pages/About"));
const VerifyOtp = lazy(() => import("./pages/VerifyOtp"));

// Loading fallback component
const SuspenseWrapper = ({ children }) => (
  <Suspense fallback={<div className="flex h-screen items-center justify-center bg-[#0e001d] text-white">Loading...</div>}>
    {children}
  </Suspense>
);

// Define the router
const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <SuspenseWrapper><HomePage /></SuspenseWrapper> },
      { path: "login", element: <SuspenseWrapper><LoginPage /></SuspenseWrapper> },
      { path: "signup", element: <SuspenseWrapper><SignupPage /></SuspenseWrapper> },
      { path: "about", element: <SuspenseWrapper><About /></SuspenseWrapper> },
      { path: "VerifyOtp", element: <SuspenseWrapper><VerifyOtp /></SuspenseWrapper> },
      {
        path: "chatbot",
        element: <Layout />,
        children: [
          { index: true, element: <SuspenseWrapper><ChatbotPage /></SuspenseWrapper> },
        ],
      },
    ],
  },
]);

// Render the app with AuthContext and Router
ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  </React.StrictMode>
);

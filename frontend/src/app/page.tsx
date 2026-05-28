"use client";

import { useEffect, useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";
import { LoginPanel } from "@/components/LoginPanel";

const SESSION_KEY = "kanban-authenticated";

export default function Home() {
  const [authenticated, setAuthenticated] = useState(false);
  const [checkingSession, setCheckingSession] = useState(true);

  useEffect(() => {
    const isSignedIn = sessionStorage.getItem(SESSION_KEY) === "true";
    setAuthenticated(isSignedIn);
    setCheckingSession(false);
  }, []);

  const handleLogin = () => {
    sessionStorage.setItem(SESSION_KEY, "true");
    setAuthenticated(true);
  };

  const handleLogout = () => {
    sessionStorage.removeItem(SESSION_KEY);
    setAuthenticated(false);
  };

  if (checkingSession) {
    return null;
  }

  return authenticated ? (
    <div className="relative">
      <div className="absolute right-6 top-6 z-10">
        <button
          type="button"
          onClick={handleLogout}
          className="rounded-full border border-[var(--stroke)] bg-white/90 px-4 py-2 text-sm font-semibold text-[var(--navy-dark)] shadow-[var(--shadow)] transition hover:bg-[var(--surface)]"
        >
          Sign out
        </button>
      </div>
      <KanbanBoard />
    </div>
  ) : (
    <LoginPanel onSuccess={handleLogin} />
  );
}

"use client";

import { FormEvent, useState } from "react";

const validUsername = "user";
const validPassword = "password";

type LoginPanelProps = {
  onSuccess: () => void;
};

export const LoginPanel = ({ onSuccess }: LoginPanelProps) => {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError("");

    if (username === validUsername && password === validPassword) {
      onSuccess();
      return;
    }

    setError("Invalid username or password. Try user/password.");
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-[radial-gradient(circle,_rgba(32,157,215,0.08)_0%,_transparent_60%)] px-6 py-10">
      <div className="w-full max-w-md rounded-[32px] border border-[var(--stroke)] bg-white/95 p-8 shadow-[var(--shadow)] backdrop-blur">
        <div className="mb-8 text-center">
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
            Kanban Studio sign in
          </p>
          <h1 className="mt-4 text-3xl font-semibold text-[var(--navy-dark)]">
            Welcome back.
          </h1>
          <p className="mt-3 text-sm leading-6 text-[var(--gray-text)]">
            Sign in with the hardcoded demo credentials to continue.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-6">
          <label className="flex flex-col gap-2 text-sm font-semibold text-[var(--navy-dark)]">
            Username
            <input
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              placeholder="user"
              className="rounded-3xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
            />
          </label>

          <label className="flex flex-col gap-2 text-sm font-semibold text-[var(--navy-dark)]">
            Password
            <input
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              placeholder="password"
              className="rounded-3xl border border-[var(--stroke)] bg-[var(--surface)] px-4 py-3 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)]"
            />
          </label>

          {error ? (
            <div className="rounded-3xl border border-[#ff6961] bg-[#ffebea] px-4 py-3 text-sm text-[#981c1c]">
              {error}
            </div>
          ) : null}

          <button
            type="submit"
            className="rounded-full bg-[var(--primary-blue)] px-5 py-3 text-sm font-semibold text-white transition hover:bg-[#167fb8]"
          >
            Sign in
          </button>
        </form>

        <div className="mt-8 rounded-3xl border border-[var(--stroke)] bg-[var(--surface)] px-5 py-4 text-sm text-[var(--gray-text)]">
          <p>
            Demo credentials: <span className="font-semibold">user</span> / <span className="font-semibold">password</span>
          </p>
        </div>
      </div>
    </div>
  );
};

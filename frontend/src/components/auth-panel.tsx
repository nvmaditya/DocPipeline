"use client";

import React from "react";
import { useMemo, useState } from "react";

import { ApiClient } from "@/lib/api-client";
import { clearStoredToken, getStoredToken, setStoredToken } from "@/lib/auth-storage";

type Props = {
  onTokenChange?: (token: string | null) => void;
};

export function AuthPanel({ onTokenChange }: Props) {
  const [email, setEmail] = useState("student@example.com");
  const [password, setPassword] = useState("password123");
  const [status, setStatus] = useState("idle");

  const api = useMemo(() => new ApiClient(undefined, getStoredToken), []);

  async function registerUser() {
    setStatus("registering...");
    try {
      await api.register({ email, password });
      setStatus("registration complete");
    } catch (error) {
      setStatus((error as Error).message);
    }
  }

  async function loginUser() {
    setStatus("logging in...");
    try {
      const data = await api.login({ email, password });
      setStoredToken(data.access_token);
      onTokenChange?.(data.access_token);
      setStatus("login complete");
    } catch (error) {
      setStatus((error as Error).message);
    }
  }

  function logoutUser() {
    clearStoredToken();
    onTokenChange?.(null);
    setStatus("token cleared");
  }

  return (
    <section className="card grid">
      <h2>Auth</h2>
      <label>
        Email
        <input value={email} onChange={(e) => setEmail(e.target.value)} />
      </label>
      <label>
        Password
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
      </label>
      <div style={{ display: "flex", gap: "8px" }}>
        <button onClick={registerUser} type="button">
          Register
        </button>
        <button className="secondary" onClick={loginUser} type="button">
          Login
        </button>
        <button className="ghost" onClick={logoutUser} type="button">
          Clear Token
        </button>
      </div>
      <p className="status" data-testid="auth-status">
        {status}
      </p>
    </section>
  );
}

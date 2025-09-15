"use client";

import { useEffect, useRef, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

type Message = { role: "user" | "assistant"; content: string };

export default function Page() {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [apiKey, setApiKey] = useState<string>("");
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight });
  }, [messages]);

  useEffect(() => {
    const saved = typeof window !== 'undefined' ? localStorage.getItem('apiKey') : null;
    if (saved) setApiKey(saved);
  }, []);

  function persistKey(k: string) {
    setApiKey(k);
    try {
      localStorage.setItem('apiKey', k);
    } catch {}
  }

  async function send() {
    const q = input.trim();
    if (!q || loading) return;
    setLoading(true);
    setMessages((m) => [...m, { role: "user", content: q }]);
    setInput("");

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          ...(apiKey ? { "X-API-Key": apiKey } : {}),
        },
        body: JSON.stringify({ query: q, template: "default" }),
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setMessages((m) => [...m, { role: "assistant", content: data.answer }]);
    } catch (e: any) {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: `Error contacting API: ${e?.message || e}` },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function clearHistory() {
    try {
      await fetch(`${API_BASE}/clear`, {
        method: "POST",
        headers: {
          ...(apiKey ? { "X-API-Key": apiKey } : {}),
        },
      });
      setMessages([]);
    } catch {}
  }

  return (
    <div>
      <h1 style={{ marginBottom: 10 }}>RAG Assistant</h1>
      <div style={{ marginBottom: 10, opacity: 0.8, display: 'flex', gap: 12, alignItems: 'center' }}>
        <span>Backend: <code>{API_BASE}</code></span>
        <span style={{ opacity: 0.6 }}>|</span>
        <input
          value={apiKey}
          onChange={(e) => persistKey(e.target.value)}
          placeholder="API key (if required)"
          style={{ padding: 6, borderRadius: 6, border: "1px solid #444", background: "#111", color: "#eee", minWidth: 180 }}
        />
      </div>
      <div
        ref={listRef}
        style={{
          border: "1px solid #333",
          borderRadius: 8,
          padding: 12,
          height: 420,
          overflowY: "auto",
          background: "#0d0d0d",
        }}
      >
        {messages.length === 0 && (
          <div style={{ opacity: 0.7 }}>Say hi and ask a question…</div>
        )}
        {messages.map((m, i) => (
          <div key={i} style={{ margin: "10px 0" }}>
            <div style={{ fontSize: 12, opacity: 0.6 }}>{m.role}</div>
            <div style={{ whiteSpace: "pre-wrap" }}>{m.content}</div>
          </div>
        ))}
      </div>
      <div style={{ display: "flex", gap: 8, marginTop: 12 }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="Type a message"
          style={{ flex: 1, padding: 10, borderRadius: 6, border: "1px solid #444", background: "#111", color: "#eee" }}
        />
        <button onClick={send} disabled={loading} style={{ padding: "10px 16px" }}>
          {loading ? "Sending…" : "Send"}
        </button>
        <button onClick={clearHistory} style={{ padding: "10px 16px" }}>
          Clear
        </button>
      </div>
    </div>
  );
}

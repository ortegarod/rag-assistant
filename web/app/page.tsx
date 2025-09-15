import Link from "next/link";

export default function LandingPage() {
  return (
    <main style={{
      minHeight: "100vh",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      background: "#0b0b0b",
      color: "#eaeaea",
      padding: 20,
    }}>
      <div style={{ maxWidth: 720, textAlign: "center" }}>
        <h1 style={{ fontSize: 36, margin: "0 0 12px" }}>RAG Assistant</h1>
        <p style={{ opacity: 0.8, marginBottom: 24 }}>
          Private, on‑prem retrieval‑augmented chat over your documents. Simple install, fast answers, your data stays in your control.
        </p>
        <div style={{ display: "flex", gap: 12, justifyContent: "center" }}>
          <Link href="/chat" style={{
            padding: "12px 18px",
            borderRadius: 8,
            background: "#5b8cff",
            color: "white",
            textDecoration: "none",
            fontWeight: 600,
          }}>Open Chat</Link>
          <a href="/docs" style={{
            padding: "12px 18px",
            borderRadius: 8,
            border: "1px solid #333",
            color: "#eaeaea",
            textDecoration: "none",
          }}>Docs</a>
        </div>
        <div style={{ opacity: 0.6, fontSize: 12, marginTop: 18 }}>
          Tip: Set your API key inside the chat page header if required.
        </div>
      </div>
    </main>
  );
}

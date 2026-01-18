import { useState, useEffect } from "react"
import ReactMarkdown from "react-markdown"
import "./App.css"

const API = import.meta.env.VITE_API_BASE_URL

function TypingMessage({ text, onFinish }) {
  const [display, setDisplay] = useState("")

  useEffect(() => {
    let i = 0
    setDisplay("")

    const interval = setInterval(() => {
      setDisplay((prev) => prev + text[i])
      i++
      if (i >= text.length) {
        clearInterval(interval)
        onFinish()
      }
    }, 12)

    return () => clearInterval(interval)
  }, [text, onFinish])

  return <span>{display}</span>
}

export default function App() {
  const [documents, setDocuments] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")

  /* ---------- Upload PDF ---------- */
  const uploadPDF = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const form = new FormData()
    form.append("file", file)

    const res = await fetch(`${API}/api/upload/`, {
      method: "POST",
      body: form,
    })

    const data = await res.json()

    // ✅ normalize backend response
    setDocuments((prev) => [
      ...prev,
      {
        id: data.id || data.document_id,
        name: data.name || data.filename || file.name,
      },
    ])
  }

  /* ---------- Start Session ---------- */
  const startSession = async () => {
    const res = await fetch(`${API}/api/session/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        document_ids: documents.map((d) => d.id),
      }),
    })

    const data = await res.json()

    // ✅ FIXED
    const sid = data.session_id || data.id
    setSessionId(sid)

    setMessages([
      {
        role: "assistant",
        content: "Ask me anything about the PDF.",
        typing: true,
      },
    ])
  }

  /* ---------- Send Message ---------- */
  const sendMessage = async () => {
    if (!input.trim() || !sessionId) return

    setMessages((prev) => [...prev, { role: "user", content: input }])
    setInput("")

    const res = await fetch(`${API}/api/chat/${sessionId}/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: input }),
    })

    const data = await res.json()

    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: data.answer || data.response || "",
        typing: true,
      },
    ])
  }

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <h2>DocuChat</h2>
        <p>AI Document Assistant</p>

        <label className="upload">
          Upload PDF
          <input type="file" hidden accept="application/pdf" onChange={uploadPDF} />
        </label>

        {documents.length > 0 && !sessionId && (
          <button className="start" onClick={startSession}>
            Start Session
          </button>
        )}

        {documents.length > 0 && (
          <div className="docs">
            <h4>Documents</h4>
            {documents.map((d) => (
              <div key={d.id} className="doc-item">
                {d.name}
              </div>
            ))}
          </div>
        )}
      </aside>

      {/* Chat */}
      <main className="chat">
        <header>
          <h3>Hi, I am your Document Assistant</h3>
          <span>Ask anything about your documents</span>
        </header>

        <section className="messages">
          {messages.map((m, i) => (
            <div key={i} className={`msg-row ${m.role}`}>
              {m.role === "assistant" && <div className="ai-orb" />}
              <div className={`msg ${m.role}`}>
                {m.role === "assistant" ? (
                  m.typing ? (
                    <TypingMessage
                      text={m.content}
                      onFinish={() =>
                        setMessages((prev) =>
                          prev.map((x, idx) =>
                            idx === i ? { ...x, typing: false } : x
                          )
                        )
                      }
                    />
                  ) : (
                    <ReactMarkdown>{m.content}</ReactMarkdown>
                  )
                ) : (
                  m.content
                )}
              </div>
            </div>
          ))}
        </section>

        <footer className="input-wrap">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={
              sessionId ? "Message DocuChat..." : "Upload a PDF to start"
            }
            disabled={!sessionId}
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button onClick={sendMessage} disabled={!sessionId}>
            Send
          </button>
        </footer>
      </main>
    </div>
  )
}

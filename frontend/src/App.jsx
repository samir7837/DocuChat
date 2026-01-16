import { useState, useEffect } from "react"
import ReactMarkdown from "react-markdown"
import "./App.css"

/* ---------- Typing Effect ---------- */
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
    if (!file || file.type !== "application/pdf") {
      alert("Only PDF files are allowed.")
      return
    }

    const form = new FormData()
    form.append("file", file)

    const res = await fetch("http://127.0.0.1:8000/api/upload/", {
      method: "POST",
      body: form,
    })
    const data = await res.json()
    setDocuments((prev) => [...prev, data])
  }

  /* ---------- Start Session ---------- */
  const startSession = async () => {
    const res = await fetch("http://127.0.0.1:8000/api/session/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ document_ids: documents.map((d) => d.id) }),
    })
    const data = await res.json()
    setSessionId(data.session_id)

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

    const res = await fetch(
      `http://127.0.0.1:8000/api/chat/${sessionId}/`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      }
    )
    const data = await res.json()

    setMessages((prev) => [
      ...prev,
      {
        role: "assistant",
        content: data.answer,
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
          <input type="file" accept="application/pdf" hidden onChange={uploadPDF} />
        </label>

        {documents.length > 0 && !sessionId && (
          <button className="start" onClick={startSession}>
            Start Session
          </button>
        )}

        {documents.length > 0 && (
  <div className="docs">
    <h4 className="docs-title">Documents</h4>

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
          <button onClick={sendMessage}>Send</button>
        </footer>
      </main>
    </div>
  )
}

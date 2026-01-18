import { useState } from "react"
import ReactMarkdown from "react-markdown"
import "./App.css"

const API = import.meta.env.VITE_API_BASE_URL

/* ---------- Typing Effect ---------- */
function TypingMessage({ text }) {
  const [display, setDisplay] = useState("")

  useState(() => {
    let i = 0
    const interval = setInterval(() => {
      setDisplay((prev) => prev + text[i])
      i++
      if (i >= text.length) clearInterval(interval)
    }, 12)

    return () => clearInterval(interval)
  }, [text])

  return <span>{display}</span>
}

export default function App() {
  const [documents, setDocuments] = useState([])
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)

  /* ---------- Upload PDF ---------- */
  const uploadPDF = async (e) => {
    const file = e.target.files[0]
    if (!file || file.type !== "application/pdf") {
      alert("Only PDF files allowed")
      return
    }

    const form = new FormData()
    form.append("file", file)

    try {
      const res = await fetch(`${API}/api/upload/`, {
        method: "POST",
        body: form,
      })

      const data = await res.json()
      setDocuments((prev) => [...prev, data])

      setMessages([
        {
          role: "assistant",
          content: "PDF uploaded successfully. Ask me anything about it.",
        },
      ])
    } catch (err) {
      alert("Upload failed")
    }
  }

  /* ---------- Send Message ---------- */
  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage = input
    setInput("")

    setMessages((prev) => [
      ...prev,
      { role: "user", content: userMessage },
    ])

    setLoading(true)

    try {
      const res = await fetch(`${API}/api/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: userMessage,
        }),
      })

      const data = await res.json()

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer || "No response from AI.",
        },
      ])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong. Please try again.",
        },
      ])
    }

    setLoading(false)
  }

  return (
    <div className="app">
      {/* Sidebar */}
      <aside className="sidebar">
        <h2>DocuChat</h2>
        <p>AI Document Assistant</p>

        <label className="upload">
          Upload PDF
          <input
            type="file"
            accept="application/pdf"
            hidden
            onChange={uploadPDF}
          />
        </label>

        {documents.length > 0 && (
          <div className="docs">
            <h4 className="docs-title">Documents</h4>
            {documents.map((d, i) => (
              <div key={i} className="doc-item">
                {d.name || "Uploaded PDF"}
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
                  <ReactMarkdown>{m.content}</ReactMarkdown>
                ) : (
                  m.content
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="msg-row assistant">
              <div className="ai-orb" />
              <div className="msg assistant">Thinking...</div>
            </div>
          )}
        </section>

        <footer className="input-wrap">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask something about the PDF..."
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button onClick={sendMessage}>Send</button>
        </footer>
      </main>
    </div>
  )
}

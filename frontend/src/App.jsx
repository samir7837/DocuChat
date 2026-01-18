import { useState } from "react"
import ReactMarkdown from "react-markdown"
import "./App.css"

const API = import.meta.env.VITE_API_BASE_URL

export default function App() {
  const [documents, setDocuments] = useState([])
  const [activeDoc, setActiveDoc] = useState(null)
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)

  /* ---------- Upload PDF ---------- */
  const uploadPDF = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const form = new FormData()
    form.append("file", file)

    try {
      const res = await fetch(`${API}/api/upload/`, {
        method: "POST",
        body: form,
      })

      const data = await res.json()

      setDocuments([data])
      setActiveDoc(data)

      setMessages([
        {
          role: "assistant",
          content: `PDF **${data.name}** uploaded successfully. Ask me anything about it.`,
        },
      ])
    } catch {
      alert("Upload failed")
    }
  }

  /* ---------- Chat ---------- */
  const sendMessage = async () => {
    if (!input.trim() || !activeDoc) return

    const question = input
    setInput("")

    setMessages((prev) => [
      ...prev,
      { role: "user", content: question },
    ])

    setLoading(true)

    try {
      const res = await fetch(`${API}/api/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: question,
          document_id: activeDoc.id,
        }),
      })

      const data = await res.json()

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer || "No response generated.",
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
          <input type="file" hidden accept="application/pdf" onChange={uploadPDF} />
        </label>

        {activeDoc && (
          <div className="docs">
            <h4 className="docs-title">Documents</h4>
            <div className="doc-item">{activeDoc.name}</div>
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
                <ReactMarkdown>{m.content}</ReactMarkdown>
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
            placeholder={
              activeDoc
                ? "Ask something about the PDF..."
                : "Upload a PDF first"
            }
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button onClick={sendMessage}>Send</button>
        </footer>
      </main>
    </div>
  )
}

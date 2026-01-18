import { useState } from "react"
import "./App.css"

const API = import.meta.env.VITE_API_BASE_URL

export default function App() {
  const [pdfName, setPdfName] = useState("")
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)

  // =====================
  // Upload PDF
  // =====================
  const uploadPDF = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    const form = new FormData()
    form.append("file", file)

    try {
      const res = await fetch(`${API}/upload/`, {
        method: "POST",
        body: form,
      })

      const data = await res.json()

      setPdfName(data.name)

      setMessages([
        {
          role: "assistant",
          content: `PDF "${data.name}" uploaded successfully. Ask me anything about it.`,
        },
      ])
    } catch (err) {
      setMessages([
        {
          role: "assistant",
          content: "Upload failed. Please try again.",
        },
      ])
    }
  }

  // =====================
  // Send Message
  // =====================
  const sendMessage = async () => {
    if (!input.trim() || loading) return

    const question = input
    setInput("")

    setMessages((prev) => [
      ...prev,
      { role: "user", content: question },
    ])

    setLoading(true)

    try {
      const res = await fetch(`${API}/chat/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: question, // ✅ BACKEND EXPECTS THIS
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
          <input
            type="file"
            accept="application/pdf"
            hidden
            onChange={uploadPDF}
          />
        </label>

        {pdfName && (
          <div className="docs">
            <div className="docs-title">Documents</div>
            <div className="doc-item">{pdfName}</div>
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
              <div className={`msg ${m.role}`}>{m.content}</div>
            </div>
          ))}
        </section>

        <footer className="input-wrap">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask something about the PDF..."
            onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          />
          <button onClick={sendMessage}>
            {loading ? "..." : "Send"}
          </button>
        </footer>
      </main>
    </div>
  )
}

import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./AI.css";

function AI() {
  const [query, setQuery] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showWelcome, setShowWelcome] = useState(true);
  const [submitted, setSubmitted] = useState(false);
  const navigate = useNavigate();
  const name = sessionStorage.getItem("username") || "";
  let welcomeText = ("Hi " + name + ", What is your query?")

  // Scroll chat to bottom
  useEffect(() => {
    const chatDiv = document.getElementById("chat-container");
    if (chatDiv) chatDiv.scrollTop = chatDiv.scrollHeight;
  }, [messages]);

  // Initialize session ID
  useEffect(() => {
    const id = "sess_" + Math.random().toString(36).substr(2, 9);
    setSessionId(id);
  }, []);

  // Stream bot response
  const readAndDecode = async (res) => {
    const reader = res.body?.getReader();
    if (!reader) return;

    const decoder = new TextDecoder();
    let firstChunk = true;
    let StreamAnswer = "";

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value, { stream: true });
      StreamAnswer += chunk;

      if (firstChunk) {
        setLoading(false);
        firstChunk = false;
        setShowWelcome(false); // hide welcome when bot starts responding
      }

      setMessages((prev) => {
        const last = prev[prev.length - 1];
        if (last?.role === "Bot") {
          const updated = [...prev];
          updated[updated.length - 1] = { ...last, text: StreamAnswer };
          return updated;
        } else {
          return [...prev, { role: "Bot", text: StreamAnswer }];
        }
      });
    }
  };

  // Handle user submit
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setSubmitted(true);
    setLoading(true);
    setMessages((prev) => [...prev, { role: "user", text: query }]);
    setQuery("");

    const response = await fetch("http://localhost:5000/rag-query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query, session_id: sessionId }),
    });

    await readAndDecode(response);
  };

  return (
    <div className="h-screen w-full flex flex-col justify-between items-center text-white">
      {/* Home Button */}
      <div className="flex w-full mt-2 left-0">
        <button
          className="border border-red-500 p-2 rounded-full font-extralight font-sans text-2xl"
          onClick={() => setTimeout(() => navigate("/", { replace: true }), 200)}
        >
          🔙
        </button>
      </div>

      {/* Welcome message */}
      {showWelcome && (
        <div>
          {welcomeText.split("").map((char, i) => (
            <span
              key={i}
              className={`welcome-msg ${submitted ? "fade-text" : ""}`}
              style={{
                animationDelay: submitted ? `${i * 0.04}s` : `${i * 0.09}s`,
              }}
            >
              {char}
            </span>
          ))}
        </div>
      )}

      {/* Chat messages */}
      <div
        id="chat-container"
        className="chat-container w-[90%] flex-1 overflow-y-auto flex flex-col gap-2 p-4 mt-3"
      >
        {messages.map((m, i) => (
          <p
            key={i}
            className={`chats p-2 rounded-xl max-w-[70%] whitespace-pre-wrap ${
              m.role === "user" ? "user-msg" : "bot-msg"
            }`}
          >
            <b>{m.role}:</b> {m.text}
          </p>
        ))}
      </div>

      {/* Loader */}
      {loading && (
        <div className="mb-2 text-center text-white">
          <div>
            ☕ Drink Some Coffee<g>.</g><g>.</g><g>.</g>
            <div className="center">
              {[...Array(10)].map((_, i) => (
                <div key={i} className="wave" style={{ animationDelay: `${i * 0.1}s` }}></div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Input form */}
      <div className="w-full p-4 bg-gray-900 flex justify-center">
        <form className="flex w-full max-w-[600px]" onSubmit={handleSubmit}>
          <input
            className="flex-1 border-2 rounded-2xl border-white bg-black text-white p-2"
            value={query}
            placeholder="Enter your query here..."
            onChange={(e) => setQuery(e.target.value)}
          />
          <button
            className="border-2 border-white p-2 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed ml-2"
            type="submit"
            disabled={query.length < 5 || loading}
          >
            Submit
          </button>
        </form>
      </div>
    </div>
  );
}

export default AI;

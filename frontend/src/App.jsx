import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [query, setQuery] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false); // ✅ loader state

  
  useEffect(() => {
    const chatDiv = document.getElementById("chat-container");
    if(chatDiv) chatDiv.scrollTop = chatDiv.scrollHeight;
  }, [messages]);
  
  useEffect(() => {
    const id = "sess_" + Math.random().toString(36).substr(2, 9);
    setSessionId(id);
  }, []);

  const readAndDecode = async (res) => {
    const reader = res.body?.getReader();
    if (!reader) return;
  
    const decoder = new TextDecoder();
    let firstChunk = true;
    let StreamAnswer = "";
  
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
  
      // Decode bytes to string
      const chunk = decoder.decode(value, { stream: true });
  
      // Append to full answer
      StreamAnswer += chunk;
  
      // Log each chunk as it arrives
  
      if (firstChunk) {
        setLoading(false); // stop loader after first chunk
        firstChunk = false;
      }
  
      // Update messages in React
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
  
  

  const handleSubmit = async (e) => {
    setLoading(true); // start loader
    e.preventDefault();
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
    <div className="h-screen w-[100%] bg-black flex flex-col-reverse justify-between items-center text-white">
      
      <form onSubmit={handleSubmit}>
        <input
          className="min-w-[50vh] border-2 border-white bg-black p-1 m-2"
          value={query}
          placeholder="Enter your query here..."
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          className="border-2 border-solid border-white p-1 m-2"
          type="submit"
          disabled={query.length < 5 || loading}
        >
          Submit
        </button>
      </form>

      <div className="w-[90%] min-h-[10vh] flex flex-col whitespace-pre-wrap">
        {messages.map((m, i) => {
          return (
          <p key={i} className={m.role === "user" ? "user-msg" : "bot-msg"}>
            <b>{m.role}</b><b>{m.text}</b>
          </p>
        )})}

        {loading && (
          <div className="mt-4 text-center">
            <div>☕ Drink Some Coffee...</div>
            <div className="center">
              <div className="wave"></div>
              <div className="wave"></div>
              <div className="wave"></div>
              <div className="wave"></div>
              <div className="wave"></div>
              <div className="wave"></div>
              <div className="wave"></div>
              <div className="wave"></div>
              <div className="wave"></div>
              <div className="wave"></div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;

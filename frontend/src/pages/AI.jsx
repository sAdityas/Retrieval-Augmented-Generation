import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "./AI.css";
import { FontAwesomeIcon as FontAwesome } from "@fortawesome/react-fontawesome";
import { faArrowLeft  as faBack } from "@fortawesome/free-solid-svg-icons";
import Loader from "../components/Loader";
import Welcome from "../components/Welcome";
import InputForm from "../components/InputForm";
import Chat from "../components/Chat";




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
          setSubmitted(false)
          return updated;
        } else {
          setSubmitted(false)
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
        ><FontAwesome icon={ faBack } ></FontAwesome>  
        </button>
      </div>
      {/* Welcome message */}
      <Welcome showWelcome={showWelcome} welcomeText={welcomeText} submitted={submitted} />
      {/* Chat messages */}
      <Chat messages={messages} />
     <Loader loading={loading} />
      {/* Input form */}
      <InputForm 
        handleSubmit={handleSubmit}
        query={query}
        setQuery={setQuery}
        loading={loading}
        submitted={submitted} />
    </div>
  );
}

export default AI;

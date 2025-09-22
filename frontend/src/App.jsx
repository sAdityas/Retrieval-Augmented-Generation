  import React, { useState } from "react";
  import "./App.css"

  function App() {
    const [query, setQuery] = useState("");
    const [answer, setAnswer] = useState("");
    const [clicked, setClicked] = useState(false)

    const readAndDecode = async (res) => {
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      while(true) {
        const{ value,done } = await reader.read();
        if (done) break;
        setAnswer((prev) => prev + decoder.decode(value, { stream: true }))
      }
    }

    const handleSubmit = async (e) => {
      !setClicked(true)
      e.preventDefault();

      // reset answer each time
      setAnswer("");

      // 🔹 Send query via POST first
      const response = await fetch("http://localhost:5000/rag-query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      }) 
      await readAndDecode(response)
      
    };

    return (
      <div className="h-screen w-screen bg-black flex flex-col justify-center items-center text-white">
        <form
          className=""
          onSubmit={handleSubmit}
        >
          <input
            className="min-w-[50vh] border-2 border-spacing-1 border-solid border-white bg-black p-1 m-2"
            value={query}
            placeholder="Enter your query here..."
            onChange={(e) => setQuery(e.target.value)}
          />
          <button
            className="border-2 border-solid border-black p-1 m-2"
            type="submit"
          >
            Submit
          </button>
        </form>
        <div className="max-w-[70vw] min-h-[10vh] justify-center items-center bg-black">
          {!answer && clicked ? (
            <div> Drink Some Coffee
            <div class="center">
            <div class="wave"></div>
            <div class="wave"></div>
            <div class="wave"></div>
            <div class="wave"></div>
            <div class="wave"></div>
            <div class="wave"></div>
            <div class="wave"></div>
            <div class="wave"></div>
            <div class="wave"></div>
            <div class="wave"></div>
          </div>
          </div>
          ):
          (
            <p>{answer}</p>
          )}
        </div>
      </div>
    );
  }

  export default App;

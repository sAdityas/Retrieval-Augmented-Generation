import React, { useRef, useEffect } from "react";
import Home from "./pages/Home";
import AI from "./pages/AI";
import "./App.css";

function App() {
  const homeRef = useRef(null);
  const aiRef = useRef(null);


  useEffect(() => {
    const originalStyle = window.getComputedStyle(document.body).overflow;
    document.body.style.overflow = "hidden"; // stop scrolling

    return () => {
      document.body.style.overflow = originalStyle; // restore on unmount
    };
  }, []);
  // Scroll to AI
  const scrollToAI = () => {
    if (aiRef.current) {
      aiRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  // Scroll back to Home
  const scrollToHome = () => {
    if (homeRef.current) {
      homeRef.current.scrollIntoView({ behavior: "smooth" });
    }
  };

  return (
    <div className="scrollAnimate flex flex-col text-white">
      <div ref={homeRef} className="h-screen w-full">
        <Home onNavigate={scrollToAI} />
      </div>
      <div ref={aiRef} className="h-screen w-full">
        <AI onNavigate={scrollToHome} />
      </div>
    </div>
  );
}

export default App;

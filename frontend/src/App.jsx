import React from "react";
import Home from "./pages/Home";
import AI from "./pages/AI";
import "./App.css";

function App() {
  const scrollWithLock = (targetId) => {
    const section = document.getElementById(targetId);
    if (!section) return;

    const original = document.body.style.overflow;
    document.body.style.overflow = "hidden"; // lock scroll

    // Use window.scrollTo for consistent behavior
    window.scrollTo({
      top: section.offsetTop,
      behavior: "smooth",
    });

    setTimeout(() => {
      document.body.style.overflow = original; // restore scroll
    }, 800); // match animation duration
  };

  return (
    <div className="scrollAnimate text-white">
      <section id="home" className="h-screen w-full">
        <Home onNavigate={() => scrollWithLock("chat")} />
      </section>
      <section id="chat" className="h-screen w-full">
        <AI onNavigate={() => scrollWithLock("home")} />
      </section>
    </div>
  );
}

export default App;

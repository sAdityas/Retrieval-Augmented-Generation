import React from "react";
import {BrowserRouter, Routes, Route} from 'react-router-dom'
import "./App.css";
import Home from "./pages/Home";
import AI from "./pages/AI";

function App() {
  return(
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />}/>
        <Route path="/chat" element={<AI />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App;

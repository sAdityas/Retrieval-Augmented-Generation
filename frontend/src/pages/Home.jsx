import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
function Home() {
  const [name, setName] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const navigate = useNavigate()

  const onSubmit = (e) => {
    e.preventDefault(); // prevent page reload
    setSubmitted(true);
    sessionStorage.setItem('username',JSON.stringify(name))
    setTimeout(() => {
        navigate("/chat", {replace:true});
     }, 3000)
  };

  return (
    <div className="h-screen flex flex-col justify-center items-center text-white">
        <div className="absolute top-[12vh]">
        <h1 className="text-l font-serif font-light"><b className="text-2xl mr-1">T</b>rack <b className="text-2xl ml-1 mr-1">C</b>omponents <span className="123">Rag Model</span></h1>
        </div>
        {!submitted ? (<>
      <form
        onSubmit={onSubmit}
        className="flex flex-col justify-center items-start"
      >
        <label
          htmlFor="Name"
          className="relative translate-x-[14px] translate-y-[10px] bg-black"
        >
          Name
        </label>
        <input
          id="Name"
          type="text"
          value={name}
          onChange={(e) => setName(e.target.value)} // ✅ update state
          className="border-white border border-solid bg-transparent rounded-2xl w-[25vw] p-2"
        />
        <button
          type="submit"
          className="mt-4 border px-4 py-2 rounded-lg bg-transparent font-serif text-xs"
        >
          Submit
        </button>
      </form>
      </>):(
        <div>
            Welcome {name}
        </div>
      )}
      
    </div>
  );
}

export default Home;

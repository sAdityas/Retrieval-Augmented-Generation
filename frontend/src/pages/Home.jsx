import React, { useState } from "react";
// import { useNavigate } from "react-router-dom";
function Home({ onNavigate }) {
  const [name, setName] = useState("");
  const [submitted, setSubmitted] = useState(false);
  // const navigate = useNavigate()




  const onSubmit = (e) => {
    e.preventDefault(); // prevent page reload
    setSubmitted(true);
    sessionStorage.setItem('username',JSON.stringify(name))
    setTimeout(() => {
        setSubmitted(false);
        if(onNavigate) onNavigate();
      // navigate("/chat", {replace:true});
     }, 3000)
  };

  return (
    <div id="Home" className={`h-screen flex flex-col justify-center items-center text-white  `}>
        <div className="absolute top-[12vh] ">
        <h1 className={`"text-l font-serif font-light transition-all duration-300 ${submitted ?  "opacity-0 scale-50" : "opacity-100 scale-100" }""`}><b className="text-2xl mr-1">T</b>rack <b className="text-2xl ml-1 mr-1">C</b>omponents <span className="123">Rag Model</span></h1>

        </div>
        
        <div className={`transition-all duration-300 ${submitted ?  "opacity-100 scale-100" : "opacity-0 scale-100" }`}>
            <h1 className="text-2xl font-serif font-light">Welcome <b className="text-3xl font-extralight font-sans"> {name}</b></h1>
        </div>
      <form
        onSubmit={onSubmit}
        className={`"flex flex-col justify-center items-start transition-all duration-300  ${submitted ?  "opacity-0 scale-50" : "opacity-100 scale-100" }"`}
      >
        <label
          htmlFor="Name"
          className="block translate-x-4 bg-black translate-y-[15px] w-[50px] rounded-xl p-1"
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
          className="mx-4 border p-2 -translate-y-0.5 rounded-lg bg-transparent font-serif text-xs"
        >
          Submit
        </button>
      </form>
      </div>
  );
}

export default Home;

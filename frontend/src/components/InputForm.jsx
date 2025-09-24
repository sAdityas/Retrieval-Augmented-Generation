import React from 'react'
import { FontAwesomeIcon as FontAwesome } from "@fortawesome/react-fontawesome";
import { faReply, faCheck } from "@fortawesome/free-solid-svg-icons";


function InputForm({ handleSubmit, query, setQuery, loading, submitted }) {
  return (
    <div className="w-full p-4 bg-gray-900 flex justify-center">
  <form className="flex w-full max-w-[40vw]" onSubmit={handleSubmit}>
    <input
      className="flex-1 border-2 rounded-2xl border-white bg-black text-white p-2"
      value={query}
      placeholder="Enter your query here..."
      onChange={(e) => setQuery(e.target.value)}
    />
    <button
      className="relative border-2 border-white  px-4 rounded-xl disabled:opacity-50 disabled:cursor-not-allowed ml-2 flex items-center justify-center"
      type="submit"
      disabled={query.length < 2 || loading}
    >
      {/* Reply Icon */}
      <FontAwesome
        icon={faReply}
        className={`absolute transition-all duration-300 text-l ${
          submitted ? "opacity-0 scale-50" : "opacity-100 scale-100"
        }`}
      />
      {/* Check Icon */}
      <FontAwesome
        icon={faCheck}
        className={`absolute transition-all duration-300 text-l ${
          submitted ? "opacity-100 scale-100" : "opacity-0 scale-50"
        }`}
      />
    </button>
  </form>
</div>
  )
}

export default InputForm
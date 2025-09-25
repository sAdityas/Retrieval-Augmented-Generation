import React from 'react'

function Chat({messages}) {
  return (
    <div
        id="chat-container"
        className="chat-container w-[90%] flex-1 overflow-y-auto flex flex-col gap-2 p-4 mt-3 "
      >
        {messages.map((m, i) => (
          <p
            key={i}
            className={`chats p-2 rounded-xl max-w-[70%] whitespace-pre-wrap font-extralight font-sans ${
              m.role === "user" ? "user-msg" : "bot-msg"
            }`}
          >
             {m.text}
          </p>
        ))}
      </div>
  )
}

export default Chat
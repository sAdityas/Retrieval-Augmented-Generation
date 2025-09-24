import React from 'react'

function Welcome({showWelcome, welcomeText, submitted}) {
  return (
    <>
    {showWelcome && (
        <div className={submitted ?  "welcome-container" : ""}>
          {welcomeText.split("").map((char, i) => (
            <span
              key={i}
              className={`welcome-msg ${submitted ? "fade-text" : ""}`}
              style={{
                animationDelay: submitted ? `${i * 0.04}s` : `${i * 0.09}s`,
              }}
            >
              {char}
            </span>
          ))}
        </div>
      )}
      </>
  )
}

export default Welcome
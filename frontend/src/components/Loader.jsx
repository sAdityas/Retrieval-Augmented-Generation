import React from 'react'
import './css/Loader.css'
import '../pages/AI'

function Loader({loading}) {
  return (
    
    <div className=" mb-2 text-center bg-transparent text-white animate-pulse">
    {loading && (
        <div  id='Loader-Container'>
          ☕  Drink Some Coffee<g>.</g><g>.</g><g>.</g>
          <div className="center bg-transparent">
            {[...Array(10)].map((_, i) => (
              <div key={i} className="wave bg-transparent" style={{ animationDelay: `${i * 0.1}s` }}></div>
            ))}
          </div>
        </div>
    )}
    </div>
  )
}

export default Loader
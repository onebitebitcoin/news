import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

// 개발 환경 로그 초기화
if (import.meta.env.DEV) {
  localStorage.removeItem('debug_logs')
  console.log('[LOG] 로그 초기화')
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)

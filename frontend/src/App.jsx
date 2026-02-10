import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import HomePage from './pages/HomePage'
import BookmarksPage from './pages/BookmarksPage'
import ApiKeysPage from './pages/ApiKeysPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="bookmarks" element={<BookmarksPage />} />
          <Route path="settings/api-keys" element={<ApiKeysPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App

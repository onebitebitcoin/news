import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/layout/Layout'
import HomePage from './pages/HomePage'
import BookmarksPage from './pages/BookmarksPage'
import ApiKeysPage from './pages/ApiKeysPage'
import SourcesSettingsPage from './pages/SourcesSettingsPage'
import DashboardPage from './pages/DashboardPage'
import AddArticlePage from './pages/AddArticlePage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<HomePage />} />
          <Route path="dashboard" element={<DashboardPage />} />
          <Route path="articles/add" element={<AddArticlePage />} />
          <Route path="bookmarks" element={<BookmarksPage />} />
          <Route path="settings/api-keys" element={<ApiKeysPage />} />
          <Route path="settings/sources" element={<SourcesSettingsPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}

export default App

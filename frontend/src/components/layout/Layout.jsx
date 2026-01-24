import { Outlet } from 'react-router-dom'
import Header from './Header'
import BottomNav from './BottomNav'

export default function Layout() {
  return (
    <div className="min-h-screen bg-zinc-950">
      <Header />
      <main className="pb-20">
        <Outlet />
      </main>
      <BottomNav />
    </div>
  )
}

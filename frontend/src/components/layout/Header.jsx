import { Bitcoin, Bell } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Header() {
  return (
    <header className="sticky top-0 z-50 bg-zinc-950/95 backdrop-blur border-b border-zinc-800">
      <div className="max-w-screen-xl mx-auto px-2 sm:px-4">
        <div className="flex items-center justify-between h-14">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <Bitcoin className="w-7 h-7 text-orange-500" />
            <span className="font-bold text-lg hidden sm:inline">Bitcoin News</span>
          </Link>

          {/* Actions */}
          <div className="flex items-center gap-2">
            <button className="p-2 rounded-lg hover:bg-zinc-800 transition-colors">
              <Bell className="w-5 h-5 text-zinc-400" />
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

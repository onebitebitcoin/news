import { NavLink } from 'react-router-dom'
import { Newspaper, BarChart3, Bookmark, Settings } from 'lucide-react'

const navItems = [
  { to: '/', icon: Newspaper, label: 'News' },
  { to: '/dashboard', icon: BarChart3, label: 'Data' },
  { to: '/bookmarks', icon: Bookmark, label: 'Saved' },
  { to: '/settings/sources', icon: Settings, label: 'Settings' },
]

export default function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-zinc-900 border-t border-zinc-800 pb-safe">
      <div className="max-w-screen-xl mx-auto">
        <div className="flex justify-around items-center h-16">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              className={({ isActive }) =>
                `flex flex-col items-center gap-1 px-4 py-2 transition-colors ${
                  isActive
                    ? 'text-orange-500'
                    : 'text-zinc-400 hover:text-zinc-200'
                }`
              }
            >
              <Icon className="w-5 h-5" />
              <span className="text-xs">{label}</span>
            </NavLink>
          ))}
        </div>
      </div>
    </nav>
  )
}

import { NavLink } from 'react-router-dom'
import { Newspaper, BarChart3, Bookmark, Settings } from 'lucide-react'

const navItems = [
  { to: '/', icon: Newspaper, label: 'News' },
  { to: '/market', icon: BarChart3, label: 'Market', disabled: true },
  { to: '/bookmarks', icon: Bookmark, label: 'Saved' },
  { to: '/settings/api-keys', icon: Settings, label: 'Settings' },
]

export default function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-50 bg-zinc-900 border-t border-zinc-800 pb-safe">
      <div className="max-w-screen-xl mx-auto">
        <div className="flex justify-around items-center h-16">
          {navItems.map(({ to, icon: Icon, label, disabled }) => (
            disabled ? (
              <div
                key={to}
                className="flex flex-col items-center gap-1 px-4 py-2 text-zinc-600 cursor-not-allowed"
              >
                <Icon className="w-5 h-5" />
                <span className="text-xs">{label}</span>
              </div>
            ) : (
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
            )
          ))}
        </div>
      </div>
    </nav>
  )
}

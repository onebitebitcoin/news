export default function CategoryChips({ categories, selected, onChange }) {
  const allCategories = ['All', ...categories]

  return (
    <div className="flex gap-2 overflow-x-auto hide-scrollbar py-2 -mx-2 px-2">
      {allCategories.map((category) => {
        const isSelected = category === 'All' ? !selected : selected === category
        return (
          <button
            key={category}
            onClick={() => onChange(category === 'All' ? null : category)}
            className={`flex-shrink-0 px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
              isSelected
                ? 'bg-orange-500 text-white'
                : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
            }`}
          >
            {category}
          </button>
        )
      })}
    </div>
  )
}

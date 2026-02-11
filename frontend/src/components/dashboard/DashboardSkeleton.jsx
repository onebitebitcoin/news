function SkeletonCard() {
  return (
    <div className="bg-zinc-900 rounded-lg p-4 animate-pulse">
      <div className="flex items-center justify-between mb-3">
        <div className="h-4 w-20 bg-zinc-800 rounded" />
        <div className="h-4 w-4 bg-zinc-800 rounded" />
      </div>
      <div className="h-8 w-32 bg-zinc-800 rounded mb-2" />
      <div className="h-4 w-24 bg-zinc-800 rounded" />
    </div>
  )
}

function SkeletonCardWide() {
  return (
    <div className="bg-zinc-900 rounded-lg p-4 animate-pulse md:col-span-2">
      <div className="flex items-center justify-between mb-3">
        <div className="h-4 w-20 bg-zinc-800 rounded" />
        <div className="h-4 w-4 bg-zinc-800 rounded" />
      </div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="space-y-2">
            <div className="h-3 w-16 bg-zinc-800 rounded" />
            <div className="h-6 w-24 bg-zinc-800 rounded" />
            <div className="h-1.5 w-full bg-zinc-800 rounded" />
          </div>
        ))}
      </div>
    </div>
  )
}

export default function DashboardSkeleton() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
      <SkeletonCard />
      <SkeletonCard />
      <SkeletonCard />
      <SkeletonCard />
      <SkeletonCardWide />
    </div>
  )
}

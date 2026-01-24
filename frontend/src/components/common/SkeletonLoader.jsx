export default function SkeletonLoader() {
  return (
    <div className="bg-zinc-900 rounded-lg overflow-hidden animate-pulse">
      {/* 이미지 스켈레톤 */}
      <div className="aspect-video bg-zinc-800" />

      {/* 콘텐츠 스켈레톤 */}
      <div className="p-3 space-y-3">
        {/* 카테고리 + 소스 */}
        <div className="flex items-center gap-2">
          <div className="w-16 h-5 bg-zinc-800 rounded" />
          <div className="w-20 h-4 bg-zinc-800 rounded" />
        </div>

        {/* 제목 */}
        <div className="space-y-2">
          <div className="w-full h-5 bg-zinc-800 rounded" />
          <div className="w-3/4 h-5 bg-zinc-800 rounded" />
        </div>

        {/* 요약 */}
        <div className="space-y-2">
          <div className="w-full h-4 bg-zinc-800 rounded" />
          <div className="w-5/6 h-4 bg-zinc-800 rounded" />
        </div>

        {/* 메타 */}
        <div className="w-24 h-4 bg-zinc-800 rounded" />
      </div>
    </div>
  )
}

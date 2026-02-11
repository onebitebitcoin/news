import { Activity, Cpu, Layers, Timer } from 'lucide-react'

function formatHashrate(hashrate) {
  if (hashrate == null) return '-'
  const eh = hashrate / 1e18
  return `${eh.toFixed(1)} EH/s`
}

function formatVsizeMB(vsize) {
  if (vsize == null) return '-'
  const mb = vsize / 1_000_000
  return `${mb.toFixed(1)} MB`
}

function formatDaysFromSeconds(seconds) {
  if (seconds == null) return '-'
  const days = Math.floor(seconds / 86400)
  return `${days.toLocaleString()}d`
}

function ProgressBar({ percent, color = 'bg-blue-500' }) {
  return (
    <div className="w-full h-1.5 bg-zinc-800 rounded-full overflow-hidden">
      <div
        className={`h-full rounded-full transition-all duration-500 ${color}`}
        style={{ width: `${Math.min(percent || 0, 100)}%` }}
      />
    </div>
  )
}

function StatRow({ label, value, valueColor = 'text-white' }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-zinc-400 text-sm">{label}</span>
      <span className={`text-sm font-medium ${valueColor}`}>{value}</span>
    </div>
  )
}

export default function NetworkStatsCard({ difficulty, hashrate, mempool, halving }) {
  return (
    <div className="bg-zinc-900 rounded-lg p-4 md:col-span-2">
      <div className="flex items-center justify-between mb-3">
        <span className="text-zinc-400 text-sm font-medium">Network</span>
        <Activity className="w-4 h-4 text-zinc-500" />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Difficulty */}
        <div className="space-y-2">
          <div className="flex items-center gap-1.5">
            <Cpu className="w-3.5 h-3.5 text-zinc-500" />
            <span className="text-xs text-zinc-500 font-medium">Difficulty</span>
          </div>
          <div className="text-lg font-bold text-white">
            {difficulty?.difficulty_change != null
              ? `${difficulty.difficulty_change > 0 ? '+' : ''}${difficulty.difficulty_change}%`
              : '-'}
          </div>
          <ProgressBar percent={difficulty?.progress_percent} color="bg-purple-500" />
          <div className="flex justify-between text-xs text-zinc-600">
            <span>{difficulty?.progress_percent != null ? `${difficulty.progress_percent}%` : '-'}</span>
            <span>{difficulty?.remaining_blocks != null ? `${difficulty.remaining_blocks.toLocaleString()} blk` : '-'}</span>
          </div>
        </div>

        {/* Hashrate */}
        <div className="space-y-2">
          <div className="flex items-center gap-1.5">
            <Layers className="w-3.5 h-3.5 text-zinc-500" />
            <span className="text-xs text-zinc-500 font-medium">Hashrate</span>
          </div>
          <div className="text-lg font-bold text-white">
            {formatHashrate(hashrate?.current_hashrate)}
          </div>
          <StatRow
            label="Difficulty"
            value={hashrate?.current_difficulty != null
              ? `${(hashrate.current_difficulty / 1e12).toFixed(2)} T`
              : '-'}
            valueColor="text-zinc-300"
          />
        </div>

        {/* Mempool */}
        <div className="space-y-2">
          <div className="flex items-center gap-1.5">
            <Activity className="w-3.5 h-3.5 text-zinc-500" />
            <span className="text-xs text-zinc-500 font-medium">Mempool</span>
          </div>
          <div className="text-lg font-bold text-white">
            {mempool?.count != null ? mempool.count.toLocaleString() : '-'}
            <span className="text-xs text-zinc-500 font-normal ml-1">txs</span>
          </div>
          <StatRow
            label="Size"
            value={formatVsizeMB(mempool?.vsize)}
            valueColor="text-zinc-300"
          />
        </div>

        {/* Halving */}
        <div className="space-y-2">
          <div className="flex items-center gap-1.5">
            <Timer className="w-3.5 h-3.5 text-zinc-500" />
            <span className="text-xs text-zinc-500 font-medium">Halving</span>
          </div>
          <div className="text-lg font-bold text-white">
            {halving?.remaining_blocks != null
              ? `${halving.remaining_blocks.toLocaleString()}`
              : '-'}
            <span className="text-xs text-zinc-500 font-normal ml-1">blk</span>
          </div>
          <ProgressBar percent={halving?.progress_percent} color="bg-amber-500" />
          <div className="flex justify-between text-xs text-zinc-600">
            <span>{halving?.progress_percent != null ? `${halving.progress_percent}%` : '-'}</span>
            <span>{formatDaysFromSeconds(halving?.remaining_time)}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

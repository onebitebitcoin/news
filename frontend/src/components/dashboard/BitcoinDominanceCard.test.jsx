import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import BitcoinDominanceCard from './BitcoinDominanceCard'

describe('BitcoinDominanceCard', () => {
  it('도미넌스 값이 있으면 퍼센트와 상태를 표시한다', () => {
    render(<BitcoinDominanceCard dominance={58.76} />)

    expect(screen.getByText('BTC Dominance')).toBeInTheDocument()
    expect(screen.getByText('58.76%')).toBeInTheDocument()
    expect(screen.getByText('Dominant')).toBeInTheDocument()
  })

  it('도미넌스 값이 없으면 대시를 표시한다', () => {
    render(<BitcoinDominanceCard dominance={null} />)

    expect(screen.getAllByText('-').length).toBeGreaterThan(0)
  })
})

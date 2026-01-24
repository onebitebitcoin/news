import { render, screen, fireEvent } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { describe, it, expect, vi } from 'vitest'
import FeedCard from './FeedCard'

const mockItem = {
  id: 'test-001',
  source: 'Bitcoin Magazine',
  title: 'Test Bitcoin Article Title',
  summary: 'This is a test summary for the article.',
  url: 'https://example.com/test',
  author: 'Test Author',
  published_at: new Date().toISOString(),
  category: 'Market',
  image_url: 'https://example.com/image.jpg',
  is_bookmarked: false,
}

const renderWithRouter = (component) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  )
}

describe('FeedCard', () => {
  it('renders article title', () => {
    renderWithRouter(<FeedCard item={mockItem} />)
    expect(screen.getByText('Test Bitcoin Article Title')).toBeInTheDocument()
  })

  it('renders source name', () => {
    renderWithRouter(<FeedCard item={mockItem} />)
    expect(screen.getByText('Bitcoin Magazine')).toBeInTheDocument()
  })

  it('renders category badge', () => {
    renderWithRouter(<FeedCard item={mockItem} />)
    expect(screen.getByText('Market')).toBeInTheDocument()
  })

  it('renders summary', () => {
    renderWithRouter(<FeedCard item={mockItem} />)
    expect(screen.getByText('This is a test summary for the article.')).toBeInTheDocument()
  })

  it('calls onBookmark when bookmark button clicked', () => {
    const handleBookmark = vi.fn()
    renderWithRouter(<FeedCard item={mockItem} onBookmark={handleBookmark} />)

    const bookmarkButtons = screen.getAllByRole('button')
    const bookmarkButton = bookmarkButtons[0]
    fireEvent.click(bookmarkButton)

    expect(handleBookmark).toHaveBeenCalledWith('test-001')
  })

  it('renders external link', () => {
    renderWithRouter(<FeedCard item={mockItem} />)

    const link = screen.getByRole('link', { name: '' })
    expect(link).toHaveAttribute('href', 'https://example.com/test')
    expect(link).toHaveAttribute('target', '_blank')
  })

  it('shows filled bookmark icon when bookmarked', () => {
    const bookmarkedItem = { ...mockItem, is_bookmarked: true }
    renderWithRouter(<FeedCard item={bookmarkedItem} />)

    const bookmarkButtons = screen.getAllByRole('button')
    const bookmarkButton = bookmarkButtons[0]
    expect(bookmarkButton).toHaveClass('bg-orange-500/20')
  })
})

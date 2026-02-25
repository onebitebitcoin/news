import { MemoryRouter } from 'react-router-dom'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import SourcesSettingsPage from './SourcesSettingsPage'

const { mockAdminApi } = vi.hoisted(() => ({
  mockAdminApi: {
    getCustomSources: vi.fn(),
    analyzeCustomSource: vi.fn(),
    createCustomSource: vi.fn(),
    updateCustomSource: vi.fn(),
    deleteCustomSource: vi.fn(),
    reanalyzeCustomSource: vi.fn(),
  },
}))

vi.mock('../api/feed', () => ({
  adminApi: mockAdminApi,
}))

vi.mock('../api/client', () => ({
  extractApiError: (err) => ({ message: err?.message || 'error', detail: null, type: null, status: null }),
}))

describe('SourcesSettingsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockAdminApi.getCustomSources.mockResolvedValue({ sources: [] })
    mockAdminApi.analyzeCustomSource.mockResolvedValue({
      draft: {
        slug_suggestion: 'custom-optech',
        name: 'Custom Optech',
        list_url: 'https://example.com/news',
        fetch_mode: 'scrape',
        extraction_rules: { strategy: 'hybrid_link_discovery', max_items: 5 },
        normalization_rules: {},
        ai_model: 'gpt-5-mini',
      },
      preview_items: [
        {
          title: 'Test title',
          url: 'https://example.com/a1',
          published_at: '2026-02-25T00:00:00Z',
          summary: 'summary',
          image_url: null,
        },
      ],
      warnings: [],
      validation_errors: [],
      is_valid: true,
    })
    mockAdminApi.createCustomSource.mockResolvedValue({ id: 1 })
  })

  it('analyzes and saves custom source', async () => {
    render(
      <MemoryRouter>
        <SourcesSettingsPage />
      </MemoryRouter>
    )

    await waitFor(() => expect(mockAdminApi.getCustomSources).toHaveBeenCalled())

    fireEvent.change(screen.getByPlaceholderText('Source name'), {
      target: { value: 'Custom Optech' },
    })
    fireEvent.change(screen.getByPlaceholderText('https://example.com/news'), {
      target: { value: 'https://example.com/news' },
    })

    fireEvent.click(screen.getByRole('button', { name: /Analyze/i }))

    await waitFor(() => expect(mockAdminApi.analyzeCustomSource).toHaveBeenCalled())
    expect(await screen.findByText('분석 결과 미리보기')).toBeInTheDocument()

    fireEvent.click(screen.getByRole('button', { name: /소스 저장/i }))

    await waitFor(() => expect(mockAdminApi.createCustomSource).toHaveBeenCalled())
  })
})

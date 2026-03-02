import client from './client'

const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

export const audioApi = {
  getList: async () => {
    const { data } = await client.get('/audio')
    return data
  },

  upload: async (formData) => {
    const { data } = await client.post('/audio/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return data
  },

  update: async (id, data) => {
    const { data: res } = await client.patch(`/audio/${id}`, data)
    return res
  },

  delete: async (id) => {
    const { data } = await client.delete(`/audio/${id}`)
    return data
  },

  getStreamUrl: (id) => `${BASE_URL}/audio/${id}/stream`,

  getReferences: async (audioId) => {
    const { data } = await client.get(`/audio/${audioId}/references`)
    return data
  },

  addReference: async (audioId, { url, title }) => {
    const { data } = await client.post(`/audio/${audioId}/references`, { url, title })
    return data
  },

  deleteReference: async (audioId, refId) => {
    const { data } = await client.delete(`/audio/${audioId}/references/${refId}`)
    return data
  },
}

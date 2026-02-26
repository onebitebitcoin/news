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

  delete: async (id) => {
    const { data } = await client.delete(`/audio/${id}`)
    return data
  },

  getStreamUrl: (id) => `${BASE_URL}/audio/${id}/stream`,
}

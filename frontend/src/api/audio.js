import client from './client'

const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1'

export const audioApi = {
  getList: () => client.get('/audio'),

  upload: (formData) =>
    client.post('/audio/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),

  delete: (id) => client.delete(`/audio/${id}`),

  getStreamUrl: (id) => `${BASE_URL}/audio/${id}/stream`,
}

import axios from 'axios'

const BASE_URL = 'http://localhost:8000/api'

class ApiService {
  constructor() {
    this.api = axios.create({
      baseURL: BASE_URL,
      headers: {
        'Content-Type': 'application/json'
      }
    })
    
    this.token = null
  }

  setToken(token) {
    this.token = token
    if (token) {
      this.api.defaults.headers.Authorization = `Bearer ${token}`
    } else {
      delete this.api.defaults.headers.Authorization
    }
  }

  async login(credentials) {
    const response = await this.api.post('/login', credentials)
    return response.data
  }

  async getCurrentUser() {
    const response = await this.api.get('/me')
    return response.data
  }

  async getMetrics(filters = {}) {
    // Remove empty filters
    const cleanFilters = {}
    Object.keys(filters).forEach(key => {
      if (filters[key] !== '' && filters[key] !== null && filters[key] !== undefined) {
        cleanFilters[key] = filters[key]
      }
    })

    const response = await this.api.post('/metrics', cleanFilters)
    return response.data
  }
}

export const api = new ApiService()
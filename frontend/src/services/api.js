import axios from 'axios'
const apiUrl = import.meta.env.VITE_API_URL;

// Create axios instance with base configuration
const api = axios.create({
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Set base URL based on environment
if (import.meta.env.DEV) {
  // Development: use localhost
  api.defaults.baseURL = 'http://localhost:8000'
} else {
  // Production: use current host
  api.defaults.baseURL = `${window.location.protocol}//${window.location.host}`
}

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`)
    return config
  },
  (error) => {
    console.error('API Request Error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`)
    return response
  },
  (error) => {
    console.error('API Response Error:', error.response?.status, error.response?.data)
    
    // Handle common error scenarios
    if (error.response?.status === 404) {
      throw new Error('Resource not found')
    } else if (error.response?.status === 500) {
      throw new Error('Server error. Please try again later.')
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Request timeout. Please check your connection.')
    } else if (!error.response) {
      throw new Error('Network error. Please check your connection.')
    }
    
    return Promise.reject(error)
  }
)

// API functions
export const createRoom = async () => {
  try {
    const response = await api.post('/create-room')
    return response.data
  } catch (error) {
    console.error('Error creating room:', error)
    throw error
  }
}

export const getRoomStatus = async (roomId) => {
  try {
    const response = await api.get(`/room/${roomId}/status`)
    return response.data
  } catch (error) {
    console.error('Error getting room status:', error)
    throw error
  }
}

export const getServerHealth = async () => {
  try {
    const response = await api.get('/')
    return response.data
  } catch (error) {
    console.error('Error checking server health:', error)
    throw error
  }
}

// Export the axios instance for custom requests
export default api
import axios from 'axios'

const axiosInstance = axios.create({
    baseURL: 'http://localhost:8000/api/v1'
})

// Uses the refresh token to get a new access token
const refreshAccessToken = async () => {
    const refresh = localStorage.getItem('refresh_token')
    const response = await axios.post('http://localhost:8000/api/v1/auth/refresh/', {
        refresh
    })
    return response.data.access
}

axiosInstance.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

axiosInstance.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            try {
                // Attempt to get a new access token
                const newToken = await refreshAccessToken()
                localStorage.setItem('access_token', newToken)

                // Retry the original failed request with new token
                error.config.headers.Authorization = `Bearer ${newToken}`
                return axiosInstance(error.config)
            } catch (err) {
                // Refresh failed - force login
                localStorage.removeItem('access_token')
                localStorage.removeItem('refresh_token')
                window.location.href = '/login'
            }
        }
        return Promise.reject(error)
    }
)

export default axiosInstance
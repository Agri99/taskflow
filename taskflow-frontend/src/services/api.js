import axiosInstance from "./axiosInstance"
import axios from "axios"

// Retrives the stored JWT token from localStorage
const getToken = () => localStorage.getItem('access_token')

// Fetches all tasks for the authenticated user
// Returns the paginated response object from Django
export const fetchTasks = async () => {
    const response = await axiosInstance.get('/tasks/')
    return response.data
}

// Send credentials to Django and returns the token pair
export const loginUser = async (username, password) => {
    const response = await axios.post('http://localhost:8000/api/v1/auth/login/', {
        username, password
    })
    return response.data
}

// Fetches a single task by ID
export const fetchTask = async (id) => {
    const response = await axiosInstance.get(`/tasks/${id}/`)
    return response.data
}

// Fetches all comments for a specific task
// Fetches all comments for a specific task
export const fetchComments = async (taskId) => {
    const response = await axiosInstance.get(`/tasks/${taskId}/comments/`)
    return response.data
}

export const createComment = async (taskId, content) => {
    const response = await axiosInstance.post(`/tasks/${taskId}/comments/`, { content })
    return response.data
}

export const getCurrentUserID = () => {
    const token = getToken()
    if (!token) return null
    const payload = JSON.parse(atob(token.split('.')[1]))
    return Number(payload.user_id)
}

export const deleteComment = async (taskId, commentId) => {
    const response = await axiosInstance.delete(`/tasks/${taskId}/comments/${commentId}/`)
    return response.data
}
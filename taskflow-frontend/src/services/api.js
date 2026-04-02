import axiosInstance from "./axiosInstance"
import axios from "axios"

// Retrives the stored JWT token from localStorage
const getToken = () => localStorage.getItem('access_token')

// Fetches all tasks for the authenticated user
// Returns the paginated response object from Django
export const fetchTasks = async (next) => {
    const url = next ? next : 'http://localhost:8000/api/v1/tasks/'
    const response = await axios.get(url, {
        headers: { Authorization: `Bearer ${localStorage.getItem('access_token')}`}
    })
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

// Fetches all comments from a specific task
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

export const canViewAudit = () => {
    const token = getToken()
    if (!token) return false
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.can_view_audit || false
}

export const deleteComment = async (taskId, commentId) => {
    const response = await axiosInstance.delete(`/tasks/${taskId}/comments/${commentId}/`)
    return response.data
}

// Fetch a single comment from a specific task to be updated
export const updateComment = async (taskId, commentId, content) => {
    const response = await axiosInstance.patch(`/tasks/${taskId}/comments/${commentId}/`, {
        content
    })
    return response.data
}


// Fetch every tasks scooped by RBAC permission
export const fetchAuditLogs = async () => {
    const response = await axiosInstance.get('/rbac/audit/')
    return response.data
}
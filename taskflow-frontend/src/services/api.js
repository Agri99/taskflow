import axiosInstance from "./axiosInstance"
import axios from "axios"

const base_url = 'http://localhost:8000/api/v1'

// Retrives the stored JWT token from localStorage
const getToken = () => localStorage.getItem('access_token')

// Fetches all tasks for the authenticated user
// Returns the paginated response object from Django
export const fetchTasks = async (next) => {
    const url = next
    ? next.replace('http://localhost:8000/api/v1', '')
    : '/tasks/'
    const response = await axiosInstance.get(url)
    return response.data
}

// Send credentials to Django and returns the token pair
export const loginUser = async (username, password) => {
    const response = await axios.post(`${base_url}/auth/login/`, {
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
    try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        return Number(payload.user_id)
    } catch {
        return null
    }
}

export const canViewAudit = () => {
    const token = getToken()
    if (!token) return false
    try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        return payload.can_view_audit || false
    } catch {
        return null
    }
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
export const fetchAuditLogs = async (next) => {
    const url = next
    ? next.replace('http://localhost:8000/api/v1')
    : '/rbac/audit'
    const response = await axiosInstance.get(url)
    return response.data
}

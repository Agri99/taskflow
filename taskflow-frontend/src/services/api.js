// Base URL for all API calls
const BASE_URL = 'http://localhost:8000/api/v1'

// Retrives the stored JWT token from localStorage
const getToken = () => localStorage.getItem('access_token')

// Fetches all tasks for the authenticated user
// Returns the paginated response object from Django
export const fetchTasks = async () => {
    const response = await fetch(`${BASE_URL}/tasks/`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`,
        }
    })

    // Check if request was successful before touching the data
    if (!response.ok) {
        const error = await response.json()
        throw new Error(error.message || 'Failed to fetch tasks')
    }

    const data = await response.json()
    return data
}

// Send credentials to Django and returns the token pair
export const loginUser = async (username, password) => {
    const response = await fetch(`${BASE_URL}/auth/login/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password })
    })

    if (!response.ok) {
        throw new Error('Invalid credentials')
    }

    return await response.json() // returns { access, refresh }
}

// Fetches a single task by ID
export const fetchTask = async (id) => {
    const response = await fetch(`${BASE_URL}/tasks/${id}`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`,
        }
    })

    if (!response.ok) {
        throw new Error('Failed to fetch task')
    }

    return await response.json()
}
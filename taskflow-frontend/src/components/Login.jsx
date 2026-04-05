import { useState } from "react"
import { loginUser } from "../services/api"
import { useLocation, useNavigate } from "react-router-dom"

function Login() {
    const [user, setUser] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState(null)

    const location = useLocation()
    const from = location.state?.from?.pathname || '/tasks'

    const navigate = useNavigate()

    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            const data = await loginUser(user, password)
            localStorage.setItem('access_token', data.access)
            localStorage.setItem('refresh_token', data.refresh)
            navigate(from)
        }catch (err) {
            setError(err.message)
        }
    }

    return (
    
        <form onSubmit={handleSubmit}>
            {error && <p style={{color: 'red'}}>{error}</p>}
            <label>Username</label>
            <input type="text" value={user} onChange={(e) => setUser(e.target.value)}/>
        
            <label>Password</label>
            <input type="password"  value={password} onChange={(e) => setPassword(e.target.value)}/>
        
            <button type="submit">Login</button>
        </form>
    
    )
}

export default Login

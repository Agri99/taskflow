import { Navigate } from "react-router-dom"

function ProtectedRoute({ children, permissionCheck }) {
    const token = localStorage.getItem('access_token')

    if (!token) {
        return <Navigate to='/login' />
    } 

    if (permissionCheck && !permissionCheck()) {
        return <Navigate to ='/tasks' />
    }

    return children
}

export default ProtectedRoute
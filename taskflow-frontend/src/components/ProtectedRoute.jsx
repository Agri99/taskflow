import { Navigate, useLocation } from "react-router-dom"

function ProtectedRoute({ children, permissionCheck }) {
    const token = localStorage.getItem('access_token')
    const location = useLocation()

    if (!token) {
        return <Navigate to='/login' state={{ from: location }} />
    } 

    if (permissionCheck && !permissionCheck()) {
        return <Navigate to ='/tasks' />
    }

    return children
}

export default ProtectedRoute
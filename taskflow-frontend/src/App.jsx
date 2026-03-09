import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Login from './components/Login'
import TaskList from './components/TaskList'
import ProtectedRoute from './components/ProtectedRoute'

function App() {
    return (
      // BrowserRouter: enables routing for the whole app
      <BrowserRouter>
          <Routes>
              <Route path='/login' element={<Login />} />
              <Route path='/tasks' element={
                <ProtectedRoute>
                  <TaskList />
                </ProtectedRoute>
              } />
          </Routes>
      </BrowserRouter>

    )
}

export default App
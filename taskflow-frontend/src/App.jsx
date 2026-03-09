import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Login from './components/Login'
import TaskList from './components/TaskList'
import TaskDetail from './components/TaskDetail'
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
              <Route path='/tasks/:id' element={
                <ProtectedRoute>
                  <TaskDetail />
                </ProtectedRoute>
              } />
          </Routes>
      </BrowserRouter>

    )
}

export default App
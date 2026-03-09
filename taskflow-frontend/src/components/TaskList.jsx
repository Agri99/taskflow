import { useState, useEffect } from "react"
import { fetchTasks } from "../services/api"

function TaskList() {
    const [tasks, setTasks] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
      const  loadTasks = async () => {
          try {
              const data = await fetchTasks()
              setTasks(data.results)
          } catch (err) {
              setError(err.message)
          }
      }
      loadTasks()
  }, [])

  return(
    <div>
        <h1>TaskFlow</h1>
        {error && <p style={{color:'red'}}>{error}</p>}
        {tasks.map((task) => (
            <div key={task.id}>
                <h3>{task.title}</h3>
                <p>{task.status_display}</p>
            </div>
        ))}
    </div>
  )
}

export default TaskList
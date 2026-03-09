import { useParams } from "react-router-dom"
import { useEffect, useState } from "react"
import { fetchTask } from "../services/api"

function TaskDetail() {
    const {id} = useParams()
    const [task, setTask] = useState({})
    const [error, setError] = useState(null)

    useEffect(() => {
        const loadTask = async () => {
            try {
                const data = await fetchTask(id)
                setTask(data)
            } catch (err) {
                setError(err.message)
            }
        }
        loadTask()
    }, [])

    return(
        <div>
            {error && <p style={{color:'red'}}>{error}</p>}
            <div key={task.id}>
                <h1>{task.title}</h1>
                <p>{task.description}</p>
                <p>Status: {task.status_display}</p>
                <p>Priority: {task.priority_display}</p>
            </div>
            <div>
                <h3>Comments</h3>
            </div>
        </div>
    ) 
}

export default TaskDetail
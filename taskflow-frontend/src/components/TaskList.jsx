import { fetchTasks, canViewAudit } from "../services/api"
import { Link } from "react-router-dom"
import { useEffect, useState } from "react"

function TaskList() {
    const [tasks, setTasks] = useState([])
    const [nextPage, setNextPage] = useState(null)
    const [error, setError] = useState(null)

    useEffect(() => {
        const loadTasks = async () => {
            try {
                const data = await fetchTasks()
                setTasks(data.results)
                setNextPage(data.next) // Store the next page URL
            } catch (err) {
                setError(err.message)
                console.error(err)
            }
        }
        loadTasks()
    }, [])

    const handlePageLoad = (newTasks) => {
        setTasks(prev => [...prev, newTasks])
    }

    const loadMore = async () => {
        const data = await fetchTasks(nextPage)
        handlePageLoad(data.results)
        setNextPage(data.next) // Update nextPage for the page after that
    }

    return(
        <div>
            <h1>TaskFlow</h1>
            {error && <p style={{color:'red'}}>{error}</p>}
            {tasks.map((task) => (
                <div key={task.id}>
                    <h3>
                        <Link to={`/tasks/${task.id}`}>{task.title}</Link>
                    </h3>
                    <p>{task.status_display}</p>
                </div>
            ))}
            {nextPage && <button onClick={loadMore}>Load More</button>}
            { canViewAudit() && <Link to={`/rbac/audit/`}>Audit</Link>}
        </div>
  )
}

export default TaskList
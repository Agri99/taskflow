import { fetchTasks, canViewAudit } from "../services/api"
import { Link } from "react-router-dom"
import useFetch from "../hooks/useFetch"

function TaskList() {
    const { data, error } = useFetch(fetchTasks, { results: [] })

  return(
    <div>
        <h1>TaskFlow</h1>
        {error && <p style={{color:'red'}}>{error}</p>}
        {data.results.map((task) => (
            <div key={task.id}>
                <h3>
                    <Link to={`/tasks/${task.id}`}>{task.title}</Link>
                </h3>
                <p>{task.status_display}</p>
            </div>
        ))}
        { canViewAudit() && <Link to={`/rbac/audit/`}>Audit</Link>}
    </div>
  )
}

export default TaskList
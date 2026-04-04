import { fetchTasks, canViewAudit } from "../services/api"
import { Link } from "react-router-dom"
import usePagination from "../hooks/usePagination"

function TaskList() {

    const {tasks, error, loadMore, nextPage} = usePagination(fetchTasks)

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
import { fetchAuditLogs } from "../services/api"
import usePagination from "../hooks/usePagination"

function AuditLog() {

    const {tasks, error, loadMore, nextPage} = usePagination(fetchAuditLogs)

    return(
        <div>
            <h1>Audit Logs</h1>
            {error && <p style={{color:'red'}}>{error}</p>}
            {tasks.map((log) => (
                <div key={log.id}>
                    <h3>{log.actor_username}</h3>
                    <p>{log.timestamp}</p>
                    <p>{log.action}</p>
                </div>
            ))}
            {nextPage && <button onClick={loadMore}>Load More</button>}
        </div>
    )
}

export default AuditLog
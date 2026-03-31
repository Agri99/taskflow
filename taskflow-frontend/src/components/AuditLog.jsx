import { fetchAuditLogs } from "../services/api"
import useFetch from "../hooks/useFetch"

function AuditLog() {
    const { data, error } = useFetch(fetchAuditLogs, {results: []})

    return(
        <div>
            <h1>Audit Logs</h1>
            {error && <p style={{color:'red'}}>{error}</p>}
            {data.results.map((task) => (
                <div key={task.id}>
                    <h3>{task.actor_username}</h3>
                    <p>{task.timestamp}</p>
                    <p>{task.action}</p>
                </div>
            ))}
        </div>
    )
}

export default AuditLog
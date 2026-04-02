import { fetchAuditLogs } from "../services/api"
import { useEffect, useState } from "react"

function AuditLog() {
    const [logs, setLogs] = useState([])
    const [nextPage, setNextPage] = useState(null)
    const [error, setError] = useState(null)

    useEffect(() => {
        const loadLogs = async () => {
            try {
                const data = await fetchAuditLogs()
                setLogs(data.results)
                setNextPage(data.next) // Store the next page URL
            } catch (err) {
                setError(err.message)
            }
        }
        loadLogs()
    }, [])

    const handlePageLoad = (newLogs) => {
        setLogs(prev => [...prev, ...newLogs])
    }

    const loadMore = async () => {
        const data = await fetchAuditLogs(nextPage)
        handlePageLoad(data.results)
        setNextPage(data.next) // Update nextPage
    }

    return(
        <div>
            <h1>Audit Logs</h1>
            {error && <p style={{color:'red'}}>{error}</p>}
            {logs.map((log) => (
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
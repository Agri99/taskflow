import { useParams } from "react-router-dom"
import { fetchTask } from "../services/api"
import useFetch from "../hooks/useFetch"

function TaskDetail() {
    const {id} = useParams()
    const { data, error } = useFetch(() => fetchTask(id), {})

    return(
        <div>
            {error && <p style={{color:'red'}}>{error}</p>}
            <div key={data.id}>
                <h1>{data.title}</h1>
                <p>{data.description}</p>
                <p>Status: {data.status_display}</p>
                <p>Priority: {data.priority_display}</p>
            </div>
            <div>
                <h3>Comments</h3>
            </div>
        </div>
    ) 
}

export default TaskDetail
import { useParams } from "react-router-dom"
import { fetchComments, fetchTask } from "../services/api"
import useFetch from "../hooks/useFetch"
import { useEffect, useState } from "react"
import CommentForm from "./CommentForm"

function TaskDetail() {
    const {id} = useParams()
    const { data: task, error: taskError } = useFetch(() => fetchTask(id), {})
    const [comments, setComments] = useState([])

    useEffect(() => {
        const loadComments = async () => {
            try {
                const data = await fetchComments(id)
                setComments(data.results)
            } catch (err) {
                console.error(err) 
            }
        }
        loadComments()
    }, [id])

    const handleCommentCreated = (newComment) => {
        setComments(prev => [...prev, newComment])
        console.log(newComment)
    }

    return(
        <div>
            {taskError && <p style={{color:'red'}}>{error}</p>}
            <div key={task.id}>
                <h1>{task.title}</h1>
                <p>{task.description}</p>
                <p>Status: {task.status_display}</p>
                <p>Priority: {task.priority_display}</p>
            </div>
            <div>
                <h3>Comments</h3>
                <CommentForm taskId={id} onCommentCreated={handleCommentCreated}/>
                {comments.length === 0
                    ? <p>No comments yet.</p>
                    : comments.map((comment) => (
                    <ul key={comment.id}>
                        <li>{comment.author_username}</li>
                        <li>{comment.content}</li>
                    </ul>
                    ))}
            </div>
        </div>
    ) 
}

export default TaskDetail
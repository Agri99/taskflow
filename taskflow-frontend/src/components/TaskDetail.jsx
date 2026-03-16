import { useParams } from "react-router-dom"
import { fetchComments, fetchTask, getCurrentUserID } from "../services/api"
import useFetch from "../hooks/useFetch"
import { useEffect, useState } from "react"
import CommentForm from "./CommentForm"

const currentUserID = getCurrentUserID()

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

    const handleDeleteComment = (deletedComment) => {
        setComments(comments.filter((comment) => comment.id !== deletedComment.id))
    }

    const isWithinEditWindow = (created_at) => {
        const now = new Date()
        const created = new Date(created_at)

        const diffInMs = now - created

        const minutesInMs = 15 * 60 * 1000

        return diffInMs <= minutesInMs
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
                        <div>
                            <p>{comment.content}</p>
                            <strong>{comment.author_username}</strong>
                            <small>
                                <span>{new Date(comment.created_at).toLocaleString()}</span>
                                {comment.is_edited == true &&
                                <span>(edited)</span>
                                }
                            </small>
                            {/* Delete: author only */}
                            {comment.author === currentUserID && (
                                <button onClick={() => handleDeleteComment(comment)}>Delete</button>
                            )}
                            {/* Edit: author only AND within edit window */}
                            {comment.author === currentUserID && isWithinEditWindow(comment.created_at) && (
                                <button>Edit</button>
                            )}
                        </div>
                    </ul>
                    ))}
            </div>
        </div>
    ) 
}

export default TaskDetail
import { useParams } from "react-router-dom"
import { fetchComments, fetchTask, getCurrentUserID, updateComment, deleteComment } from "../services/api"
import useFetch from "../hooks/useFetch"
import { useEffect, useState } from "react"
import CommentForm from "./CommentForm"

const currentUserID = getCurrentUserID()

function TaskDetail() {
    const {id} = useParams()
    const { data: task, error: taskError, loading } = useFetch(() => fetchTask(id), {})
    const { title, description, status_display, priority_display } = task || {}
    const [comments, setComments] = useState([])
    const [editingId, setEditingId] =  useState (null)
    const [editContent, setEditContent] = useState("")
    const [error, setError] = useState(null)

    useEffect(() => {
        const loadComments = async () => {
            try {
                const data = await fetchComments(id)
                setComments(data.results)
            } catch (err) {
                setError(err.message)
            }
        }
        loadComments()
    }, [id])

    const handleCommentCreated = (newComment) => {
        setComments(prev => [...prev, newComment])
    }

    const handleDeleteComment = async (deletedComment) => {
        try {
            await deleteComment(id, deletedComment.id)
            setComments(comments.filter((comment) => comment.id !== deletedComment.id))
        } catch (err) {
            setError(err.message)
        }
    }

    const handleEditComment = async (commentId) => {
        try {
            const updatedComment = await updateComment(id, commentId, editContent)

            setComments(prevComments =>
                prevComments.map(c => (c.id === commentId ? updatedComment : c))
            )

            setEditingId(null)
            setEditContent("")
        } catch (err) {
            setError(err.message)
            alert("Failed to update comment.")
        }
    }

    const isWithinEditWindow = (created_at) => {
        const now = new Date()
        const created = new Date(created_at)

        const diffInMs = now - created

        const minutesInMs = 15 * 60 * 1000

        return diffInMs <= minutesInMs
    }

    if (loading) return <p>Loading...</p>

    return(
        <div>
            {taskError && <p style={{color:'red'}}>{taskError}</p>}
            {task && (
                <div key={id}>
                    <h1>{title}</h1>
                    <p>{description}</p>
                    <p>Status: {status_display}</p>
                    <p>Priority: {priority_display}</p>
                </div>
            )}
            <div>
                <h3>Comments</h3>
                <CommentForm taskId={id} onCommentCreated={handleCommentCreated}/>
                {error && <p style={{color: 'red'}}>{error}</p>}
                {comments.length === 0
                    ? <p>No comments yet.</p>
                    : comments.map((comment) => (
                    <div key={comment.id}>
                        {editingId === comment.id ? (
                            /* Edit Mode: Show the input form */
                            <div>
                                <textarea
                                    className="edit-textarea"
                                    value={editContent}
                                    onChange={(e) => setEditContent(e.target.value)}/>
                                <div className="edit-actions">
                                    <button onClick={() => handleEditComment(comment.id)}>Save</button>
                                    <button onClick={() => { setEditingId(null); setEditContent("");}}>
                                        Cancel
                                    </button>
                                </div>
                            </div>
                        ) : (
                            /* View ModeL Show the content as usual */
                            <div>
                                <p>{comment.content}</p>
                                <strong>{comment.author_username}</strong>
                                <small>
                                    <span>{new Date(comment.created_at).toLocaleString()}</span>
                                    {comment.is_edited &&
                                    <span>(edited)</span>
                                    }
                                </small>
                                {/* Delete: author only */}
                                {comment.author === currentUserID && (
                                    <button onClick={() => handleDeleteComment(comment)}>
                                        Delete
                                    </button>
                                )}
                                {/* Edit: author only AND within edit window */}
                                {comment.author === currentUserID && isWithinEditWindow(comment.created_at) && (
                                    <button onClick={() => {
                                        setEditingId(comment.id);
                                        setEditContent(comment.content);
                                    }}>
                                        Edit
                                    </button>
                                )}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    ) 
}

export default TaskDetail
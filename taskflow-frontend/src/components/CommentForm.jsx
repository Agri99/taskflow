import { useState } from "react";
import { createComment } from '../services/api'

function CommentForm({ taskId, onCommentCreated }) {
    const [content, setContent] = useState('')
    const [error, setError] = useState(null)

    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
            const newComment = await createComment(taskId, content)
            onCommentCreated(newComment) // tell TaskDetail about the new comment
            setContent('') // clear the form after submission
        } catch (err) {
            setError(err.message)
        }
    }

    return (
        <form onSubmit={handleSubmit}>
            <textarea
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder='Write a comment...'/>
            {error && <p style={{color: 'red'}}>{error}</p>}
            <button type="submit">Post Comment</button>
        </form>
    )

}

export default CommentForm
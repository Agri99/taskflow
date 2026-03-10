import { useParams } from "react-router-dom"
import { fetchComments, fetchTask } from "../services/api"
import useFetch from "../hooks/useFetch"
import { useState } from "react"

function TaskDetail() {
    const {id} = useParams()
    const { data: task, error: taskError } = useFetch(() => fetchTask(id), {})
    const { data: comments, error: commentError } = useFetch(() => fetchComments(id), { results: [] })

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
                {commentError && <p style={{color:'red'}}>{commentError}</p>}
                {comments.results.length === 0
                    ? <p>No comments yet.</p>
                    : comments.results.map((comment) => (
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
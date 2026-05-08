// taskflow-frontend/src/components/TaskFormModal.jsx

import { useState } from 'react'
import { createTask } from '../services/api'
import { useNavigate } from 'react-router-dom'

function TaskFormModal({ isOpen, onClose, onTaskCreated }) {
    const navigate = useNavigate()
    const [formData, setFormData] = useState({
        title: '',
        description: '',
        status: 'T',
        priority: 'L'
    })
    const [error, setError] = useState(null)
    const [loading, setLoading] = useState(false)

    // Handle changes to any input field
    const handleChange = (e) => {
        const { name, value } = e.target
        setFormData(prevData => ({
            ...prevData,
            [name]: value
        }))
    }

    // Handle form submission
    const handleSubmit = async (e) => {
        e.preventDefault()
        console.log('Form submitted with data:', formData)  // ADD THIS LINE
        setLoading(true)
        setError(null)

        try {
            const newTask = await createTask(formData)
        
            
            // Clear form
            setFormData({
                title: '',
                description: '',
                status: 'T',
                priority: 'L'
            })

            // Close modal
            onClose()

            // Redirect to task detail
            navigate(`/tasks/${newTask.id}`)
        } catch (err) {
            setError(err.message)
            setLoading(false)
        }
    }

    // Don't render if modal is closed
    if (!isOpen) return null

    return (
        <div className='modal-overlay' onClick={onClose}>
            <div className='modal-content' onClick={(e) => e.stopPropagation()}>
                <div className='modal-header'>
                    <h2>Create New Task</h2>
                    <button className='modal-close' onClick={onClose}>×</button>
                </div>

                <form onSubmit={handleSubmit}>
                    {error && <p style={{ color: 'red' }}>{error}</p>}

                    <div className='form-group'>
                        <label htmlFor='title'>Title *</label>
                        <input
                            type='text'
                            id='title'
                            name='title'
                            value={formData.title}
                            onChange={handleChange}
                            placeholder='Enter task title'
                            required
                        />
                    </div>

                    <div className='form-group'>
                        <label htmlFor='description'>Description *</label>
                        <textarea
                            id='description'
                            name='description'
                            value={formData.description}
                            onChange={handleChange}
                            placeholder='Enter task description'
                            required
                            rows='4'
                        />
                    </div>

                    <div className='form-row'>
                        <div className='form-group'>
                            <label htmlFor='status'>Status</label>
                            <select
                                id='status'
                                name='status'
                                value={formData.status}
                                onChange={handleChange}
                            >
                                <option value='T'>Todo</option>
                                <option value='I'>In Progress</option>
                                <option value='D'>Done</option>
                            </select>
                        </div>

                        <div className='form-group'>
                            <label htmlFor='priority'>Priority</label>
                            <select
                                id='priority'
                                name='priority'
                                value={formData.priority}
                                onChange={handleChange}
                            >
                                <option value='L'>Low</option>
                                <option value='M'>Medium</option>
                                <option value='H'>High</option>
                            </select>
                        </div>
                    </div>

                    <div className='form-actions'>
                        <button type='submit' disabled={loading}>
                            {loading ? 'Creating...' : 'Create Task'}
                        </button>
                        <button type='button' onClick={onClose}>
                            Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}

export default TaskFormModal
import { useState } from "react"
import { useEffect } from "react"

function usePagination(fetchData) {
    const [tasks, setTasks] = useState([])
    const [nextPage, setNextPage] = useState(null)
    const [error, setError] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const loadTasks = async () => {
            try {
                const tasks = await fetchData()
                setTasks(tasks.results)
                setNextPage(tasks.next) // Store the next page URL
                setLoading(false)
            } catch (err) {
                setError(err.message)
                setLoading(false)
            }
        }
        loadTasks()
    }, [])

    const handlePageLoad = (newTasks) => {
        setTasks(prev => [...prev, ...newTasks])
    }

    const loadMore = async () => {
        try {
            const tasks = await fetchData(nextPage)
            handlePageLoad(tasks.results)
            setNextPage(tasks.next) // Update nextPage
        } catch (err) {
            setError(err.message)
        }
    }

    return {tasks, error, loadMore, nextPage, loading}
}

export default usePagination
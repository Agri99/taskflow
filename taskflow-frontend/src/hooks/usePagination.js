import { useState } from "react"
import { useEffect } from "react"

function usePagination(fetchData) {
    const [tasks, setTasks] = useState([])
    const [nextPage, setNextPage] = useState(null)
    const [error, setError] = useState(null)

    useEffect(() => {
        const loadTasks = async () => {
            try {
                const tasks = await fetchData()
                setTasks(tasks.results)
                setNextPage(tasks.next) // Store the next page URL
            } catch (err) {
                setError(err.message)
            }
        }
        loadTasks()
    }, [])

    const handlePageLoad = (newTasks) => {
        setTasks(prev => [...prev, ...newTasks])
    }

    const loadMore = async () => {
        const tasks = await fetchData(nextPage)
        handlePageLoad(tasks.results)
        setNextPage(tasks.next) // Update nextPage
    }

    return {tasks, error, loadMore, nextPage}
}

export default usePagination
import { useState } from "react"
import { useEffect } from "react"

function useFetch(fetchData, initialValue = {}) {
    const [data, setData] = useState(initialValue)
    const [error, setError] = useState(null)
    const [loading, setLoading] = useState(true)
    
    useEffect(() => {
            const  loadTasks = async () => {
                try {
                    const data = await fetchData()
                    setData(data)
                    setLoading(false)
                } catch (err) {
                    setError(err.message)
                    setLoading(false)
                }
            }
            loadTasks()
    }, [])

    return {data, error}
}

export default useFetch
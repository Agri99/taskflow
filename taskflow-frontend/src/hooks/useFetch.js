import { useState } from "react"
import { useEffect } from "react"

function useFetch(fetchData, initialValue = {}) {
    const [data, setData] = useState(initialValue)
    const [error, setError] = useState(null)
    
    useEffect(() => {
            const  loadTasks = async () => {
                try {
                    const data = await fetchData()
                    setData(data)
                } catch (err) {
                    setError(err.message)
                }
            }
            loadTasks()
    }, [])

    return {data, error}
}

export default useFetch
import { useCallback, useEffect, useState } from 'react'

export function useAsync(asyncFn, deps = []) {
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  const [loading, setLoading] = useState(true)

  const run = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await asyncFn()
      setData(result)
      return result
    } catch (err) {
      setError(err)
      throw err
    } finally {
      setLoading(false)
    }
  }, deps)

  useEffect(() => {
    run().catch(() => {})
  }, [run])

  return { data, error, loading, reload: run }
}

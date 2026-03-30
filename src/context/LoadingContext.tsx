import { createContext, useContext, useState, ReactNode } from 'react'

interface LoadingContextValue {
  isLoaded: boolean
  setLoaded: () => void
}

const LoadingContext = createContext<LoadingContextValue>({
  isLoaded: false,
  setLoaded: () => {},
})

export function LoadingProvider({ children }: { children: ReactNode }) {
  const [isLoaded, setIsLoaded] = useState(false)
  return (
    <LoadingContext.Provider value={{ isLoaded, setLoaded: () => setIsLoaded(true) }}>
      {children}
    </LoadingContext.Provider>
  )
}

export function useLoading() {
  return useContext(LoadingContext)
}

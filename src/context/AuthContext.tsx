import React, { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

interface User {
  _id: string
  email: string
  name: string
}

interface AuthContextType {
  user: User | null
  loading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('token')
      if (token) {
        const response = await axios.get('http://localhost:3000/api/auth/me', {
          headers: { Authorization: `Bearer ${token}` }
        })
        setUser(response.data)
      }
    } catch (err) {
      localStorage.removeItem('token')
    } finally {
      setLoading(false)
    }
  }

  const login = async (email: string, password: string) => {
    try {
      setError(null)
      const response = await axios.post('http://localhost:3000/api/auth/login', {
        email,
        password
      })
      const { token, user } = response.data
      localStorage.setItem('token', token)
      setUser(user)
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed')
      throw err
    }
  }

  const register = async (name: string, email: string, password: string) => {
    try {
      setError(null)
      const response = await axios.post('http://localhost:3000/api/auth/register', {
        name,
        email,
        password
      })
      const { token, user } = response.data
      localStorage.setItem('token', token)
      setUser(user)
    } catch (err: any) {
      setError(err.response?.data?.message || 'Registration failed')
      throw err
    }
  }

  const logout = async () => {
    try {
      await axios.post('http://localhost:3000/api/auth/logout')
      localStorage.removeItem('token')
      setUser(null)
    } catch (err) {
      console.error('Logout error:', err)
    }
  }

  return (
    <AuthContext.Provider value={{ user, loading, error, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
} 
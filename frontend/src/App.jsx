import React, { useState, useEffect } from 'react'
import LoginForm from './components/LoginForm'
import MetricsTable from './components/MetricsTable'
import { api } from './services/api'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('token')
    if (token) {
      api.setToken(token)
      // Verify token is still valid
      api.getCurrentUser()
        .then(userData => {
          setUser(userData)
        })
        .catch(() => {
          localStorage.removeItem('token')
          api.setToken(null)
        })
        .finally(() => {
          setLoading(false)
        })
    } else {
      setLoading(false)
    }
  }, [])

  const handleLogin = async (credentials) => {
    try {
      const response = await api.login(credentials)
      localStorage.setItem('token', response.access_token)
      api.setToken(response.access_token)
      setUser(response.user)
    } catch (error) {
      throw error
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('token')
    api.setToken(null)
    setUser(null)
  }

  if (loading) {
    return (
      <div className="container">
        <div className="loading">Loading...</div>
      </div>
    )
  }

  return (
    <div className="container">
      {!user ? (
        <LoginForm onLogin={handleLogin} />
      ) : (
        <>
          <div className="user-info">
            <div>
              <strong>Welcome, {user.name}</strong>
              <br />
              <small>{user.email} ({user.role})</small>
            </div>
            <button className="btn btn-danger" onClick={handleLogout}>
              Logout
            </button>
          </div>
          <MetricsTable user={user} />
        </>
      )}
    </div>
  )
}

export default App
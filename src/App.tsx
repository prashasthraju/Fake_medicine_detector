import React from 'react'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import Home from './pages/Home'
import About from './pages/About'
import Contact from './pages/Contact'

const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main>
          <Home />
        </main>
      </div>
    ),
  },
  {
    path: '/about',
    element: (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main>
          <About />
        </main>
      </div>
    ),
  },
  {
    path: '/contact',
    element: (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <main>
          <Contact />
        </main>
      </div>
    ),
  },
])

const App = () => {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  )
}

export default App 
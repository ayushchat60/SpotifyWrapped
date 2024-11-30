import React from 'react';
import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Home from './components/Home';
import SpotifyWrappedTrivia from './components/SpotiftyWrappedTrivia';
import SpotifyCallback from './components/SpotifyCallback';
import WrappedDetail from './components/WrappedDetail';

/**
 * ProtectedRoute Component
 *
 * This component handles route protection by checking the user's authentication status.
 * If the user is authenticated, the child components are rendered. Otherwise, the user
 * is redirected to the login page.
 *
 * Props:
 * - children: The components to render if the user is authenticated.
 *
 * Returns:
 * - The children components if authenticated.
 * - A redirect to the login page if not authenticated.
 */
const ProtectedRoute = ({ children }) => {
  const isLoggedIn = localStorage.getItem("accessToken") !== null; // Check if the access token exists
  return isLoggedIn ? children : <Navigate to="/login" />;
};

/**
 * App Component
 *
 * This component defines the main routing structure of the application.
 * It uses React Router for navigation and includes protected routes for authenticated pages.
 *
 * Features:
 * - Public Routes: Login, Register, and Spotify Callback.
 * - Protected Routes: Home, Wrapped Detail, and Spotify Wrapped Trivia.
 */
function App() {
  return (
    <Router>
      <Routes>
        {/* Protected route for home */}
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        {/* Public routes for authentication */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* Spotify OAuth callback route */}
        <Route path="/callback" element={<SpotifyCallback />} />
        
        {/* Public route for the trivia game */}
        <Route path="/game" element={<SpotifyWrappedTrivia />} />
        
        {/* Protected route for Wrapped Detail page */}
        <Route
          path="/wrapped-detail/:id"
          element={
            <ProtectedRoute>
              <WrappedDetail />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

export default App;

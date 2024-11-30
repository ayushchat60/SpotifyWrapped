import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import WrappedDetail from './components/WrappedDetail';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import SpotifyCallback from './components/SpotifyCallback';
import Home from './components/Home';
import SpotifyWrappedTrivia from './components/SpotiftyWrappedTrivia';

// ProtectedRoute component to handle the logic of protecting routes
const ProtectedRoute = ({ children }) => {
  const isLoggedIn = localStorage.getItem("accessToken") !== null;
  return isLoggedIn ? children : <Navigate to="/login" />;
};

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
        {/* Login and Register are public routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        {/* Spotify callback route (assuming it's public or doesn't require auth) */}
        <Route path="/callback" element={<SpotifyCallback />} />
        <Route path="/game" element={<SpotifyWrappedTrivia />} />
        
        {/* Wrapped Detail page - Protected */}
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

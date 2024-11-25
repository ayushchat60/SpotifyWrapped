import WrappedDetail from "./components/WrappedDetail"; 
import Login from "./components/Auth/Login";
import Register from "./components/Auth/Register";
import SpotifyCallback from "./components/SpotifyCallback";
import React from 'react';
import Home from "./components/Home";
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';

function App() {
  const isLoggedIn = () => {
    const token = localStorage.getItem("accessToken");
    return token !== null;
  };

  return (
    <Router>
      <Routes>
        <Route
          path="/"
          element={isLoggedIn() ? <Home /> : <Navigate to="/login" />}
        />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/home" element={<Home />} />
        <Route path="/callback" element={<SpotifyCallback />} />
        <Route path="/wrapped-detail/:id" element={<WrappedDetail />} />
      </Routes>
    </Router>
  );
}

export default App;

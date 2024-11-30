import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

function Login() {
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false); // To handle loading state
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_BASE_URL}login/`,
        formData
      );
      // Store tokens in localStorage
      localStorage.setItem("accessToken", response.data.access);
      localStorage.setItem("refreshToken", response.data.refresh);

      // Set the default Authorization header for all future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;

      alert("Login successful!");
      navigate("/"); // Redirect to home page
    } catch (err) {
      console.error(err);
      alert("Invalid credentials! Please try again.");
      localStorage.removeItem("accessToken"); // Clear token on failure
      localStorage.removeItem("refreshToken");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-spotifyBlack">
      <div className="w-full max-w-sm bg-spotifyDark p-8 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-center text-spotifyGreen">
          Log In
        </h1>
        <form onSubmit={handleLogin} className="mt-6 space-y-4">
          <input
            type="text"
            placeholder="Username"
            required
            className="w-full px-4 py-2 bg-spotifyDark text-white border border-spotifyGreen rounded focus:outline-none focus:ring-2 focus:ring-spotifyGreenHover"
            onChange={(e) =>
              setFormData({ ...formData, username: e.target.value })
            }
          />
          <input
            type="password"
            placeholder="Password"
            required
            className="w-full px-4 py-2 bg-spotifyDark text-white border border-spotifyGreen rounded focus:outline-none focus:ring-2 focus:ring-spotifyGreenHover"
            onChange={(e) =>
              setFormData({ ...formData, password: e.target.value })
            }
          />
          <button
            type="submit"
            className={`w-full py-2 bg-spotifyGreen text-black font-bold rounded transition ${
              loading ? "opacity-50 cursor-not-allowed" : "hover:bg-spotifyGreenHover"
            }`}
            disabled={loading}
          >
            {loading ? "Logging In..." : "Log In"}
          </button>
        </form>
        <button
          onClick={() => navigate("/register")}
          className="w-full text-center mt-4 text-spotifyGreen hover:text-spotifyGreenHover transition"
        >
          Don't have an account? Register
        </button>
      </div>
    </div>
  );
}

export default Login;

import axios from "axios";
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

/**
 * Register Component
 *
 * This component renders a registration form that allows new users to create an account
 * by providing their username, email, and password. On successful registration, the user
 * is redirected to the login page.
 *
 * Features:
 * - Form inputs for username, email, and password.
 * - Handles form submission via an API call to register the user.
 * - Navigation to the login page after successful registration.
 */
function Register() {
  const [formData, setFormData] = useState({ username: "", email: "", password: "" }); // State for form data
  const navigate = useNavigate();

  /**
   * Handles the registration process.
   *
   * @param {Object} e - The event object for the form submission.
   * @returns {Promise<void>}
   */
  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${process.env.REACT_APP_API_BASE_URL}register/`, formData);
      alert("Registration successful!");
      navigate("/login");
    } catch (err) {
      console.error(err);
      alert("Error registering user!");
    }
  };

  return (
    <div className="flex justify-center items-center h-screen bg-spotifyBlack">
      <div className="w-full max-w-sm bg-spotifyDark p-8 rounded-lg shadow-md">
        <h1 className="text-3xl font-bold text-center text-spotifyGreen">Sign Up</h1>
        <form onSubmit={handleRegister} className="mt-6 space-y-4">
          <input
            type="text"
            placeholder="Username"
            className="w-full px-4 py-2 bg-spotifyDark text-white border border-spotifyGreen rounded focus:outline-none"
            onChange={(e) => setFormData({ ...formData, username: e.target.value })}
          />
          <input
            type="email"
            placeholder="Email"
            className="w-full px-4 py-2 bg-spotifyDark text-white border border-spotifyGreen rounded focus:outline-none"
            onChange={(e) => setFormData({ ...formData, email: e.target.value })}
          />
          <input
            type="password"
            placeholder="Password"
            className="w-full px-4 py-2 bg-spotifyDark text-white border border-spotifyGreen rounded focus:outline-none"
            onChange={(e) => setFormData({ ...formData, password: e.target.value })}
          />
          <button
            type="submit"
            className="w-full py-2 bg-spotifyGreen text-black font-bold rounded hover:bg-spotifyGreenHover transition">
            Register
          </button>
        </form>
        <button
          onClick={() => navigate("/login")}
          className="w-full text-center mt-4 text-spotifyGreen hover:text-spotifyGreenHover transition">
          Already have an account? Login
        </button>
      </div>
    </div>
  );
}

export default Register;

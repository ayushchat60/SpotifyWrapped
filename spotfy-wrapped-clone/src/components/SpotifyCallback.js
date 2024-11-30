import React, { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";

/**
 * SpotifyCallback Component
 *
 * This component handles the callback after the user authorizes the app in Spotify's OAuth process.
 * It retrieves the authorization code from the URL, sends it to the backend to exchange it
 * for an access token, and navigates back to the home page upon success.
 *
 * Features:
 * - Extracts the authorization code from the callback URL.
 * - Sends the code to the backend API for token exchange.
 * - Handles success and error scenarios for linking Spotify accounts.
 */
function SpotifyCallback() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    /**
     * Handles Spotify OAuth callback by extracting the authorization code
     * and sending it to the backend API to complete the linking process.
     */
    const urlParams = new URLSearchParams(location.search);
    const code = urlParams.get("code");

    if (code) {
      fetch("http://127.0.0.1:8000/api/spotify/callback/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("accessToken")}`, // Include the JWT token
        },
        body: JSON.stringify({ code }),
      })
        .then((response) => {
          if (response.ok) {
            return response.json();
          }
          throw new Error("Failed to link Spotify account");
        })
        .then((data) => {
          console.log("Spotify linked successfully:", data);
          navigate("/");
        })
        .catch((error) => {
          console.error("Error linking Spotify account:", error);
        });
    } else {
      console.error("No authorization code found in callback URL");
      navigate("/");
    }
  }, [location, navigate]);

  return <div>Linking your Spotify account...</div>;
}

export default SpotifyCallback;
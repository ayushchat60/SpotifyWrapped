import React, { useEffect } from "react";
import { useNavigate, useLocation } from "react-router-dom";

function SpotifyCallback() {
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
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

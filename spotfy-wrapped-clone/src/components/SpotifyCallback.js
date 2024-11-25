// src/SpotifyCallback.js
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

function SpotifyCallback() {
  const navigate = useNavigate();

  useEffect(() => {
    // Get the URL parameters (access token, error)
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');
    const error = params.get('error');

    if (error) {
      alert(`Error during authentication: ${error}`);
      navigate('/login');
      return;
    }

    if (code) {
      // Exchange the code for an access token
      const fetchAccessToken = async () => {
        try {
          const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}spotify/callback/`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code }),
          });

          const data = await response.json();
          if (response.ok) {
            localStorage.setItem('accessToken', data.access_token); // Save the token
            localStorage.setItem('refreshToken', data.refresh_token); // Save the refresh token
            navigate('/home'); // Redirect to the home page after successful login
          } else {
            alert('Failed to fetch access token.');
            navigate('/login');
          }
        } catch (error) {
          console.error('Error fetching access token:', error);
          navigate('/login');
        }
      };

      fetchAccessToken();
    }
  }, [navigate]);

  return (
    <div className="text-white text-center p-4">
      <h2>Spotify Authentication</h2>
      <p>Processing your login...</p>
    </div>
  );
}

export default SpotifyCallback;

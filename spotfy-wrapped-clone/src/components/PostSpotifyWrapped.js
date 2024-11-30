import axios from 'axios';
import React, { useState } from 'react';

/**
 * PostSpotifyWrapped Component
 *
 * This component displays a user's Spotify Wrapped summary, including top artists and tracks.
 * It allows the user to make their Spotify Wrapped summary public.
 *
 * Props:
 * - wrapped: An object containing details of the Spotify Wrapped summary.
 *   - id: The unique ID of the Wrapped summary.
 *   - title: The title of the Wrapped summary.
 *   - image_url: The URL of the image for the Wrapped summary.
 *   - artists: An array of the top artists for the Wrapped summary.
 *   - tracks: An array of the top tracks for the Wrapped summary.
 *   - public: A boolean indicating if the Wrapped summary is public.
 *
 * Features:
 * - Displays the Wrapped title, image, top artists, and top tracks.
 * - Allows the user to make the Wrapped public with a button click.
 */
function PostSpotifyWrapped({ wrapped }) {
  const [isPublic, setIsPublic] = useState(wrapped.public); // Tracks if the Wrapped summary is public

  /**
   * Makes the Spotify Wrapped summary public by sending a POST request to the API.
   *
   * @returns {Promise<void>}
   */
  const handleMakePublic = async () => {
    try {
      const response = await axios.post(`/api/wrapped/make-public/${wrapped.id}/`, {}, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`
        }
      });

      setIsPublic(true);
      alert('Your Spotify Wrapped is now public!');
    } catch (error) {
      console.error('Error making Wrapped public', error);
      alert('Failed to make Wrapped public');
    }
  };

  return (
    <div>
      <h1>{wrapped.title}</h1>
      <img src={wrapped.image_url} alt="Wrapped" width="200" />
      <div>
        <strong>Top Artists:</strong>
        <ul>
          {wrapped.artists.map((artist, i) => (
            <li key={i}>{artist}</li>
          ))}
        </ul>
      </div>
      <div>
        <strong>Top Tracks:</strong>
        <ul>
          {wrapped.tracks.map((track, i) => (
            <li key={i}>{track}</li>
          ))}
        </ul>
      </div>
      {!isPublic && (
        <button onClick={handleMakePublic}>Make Public</button>
      )}
      {isPublic && <p>This Wrapped is now public!</p>}
    </div>
  );
}

export default PostSpotifyWrapped;

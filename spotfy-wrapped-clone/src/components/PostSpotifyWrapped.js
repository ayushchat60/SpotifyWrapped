import React, { useState } from 'react';
import axios from 'axios';

function PostSpotifyWrapped({ wrapped }) {
  const [isPublic, setIsPublic] = useState(wrapped.public);

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

import React, { useEffect, useState } from 'react';

/**
 * PublicWrapped Component
 *
 * This component displays a list of public Spotify Wrapped summaries shared by users.
 * It fetches the public Wrapped history from the backend API and renders each summary,
 * including its title, image, top artists, and top tracks.
 *
 * Features:
 * - Fetches public Wrapped histories on component mount.
 * - Displays the title, image, and lists of top artists and tracks for each public Wrapped summary.
 */
const PublicWrapped = () => {
  const [publicHistories, setPublicHistories] = useState([]); // Stores public Wrapped histories

  /**
   * Fetches public Spotify Wrapped histories from the API.
   *
   * This function is triggered on component mount via `useEffect`.
   *
   * @returns {Promise<void>}
   */
  useEffect(() => {
    const fetchPublicHistories = async () => {
      try {
        const response = await fetch('/api/public_histories/'); // API endpoint for public Wrapped histories
        const data = await response.json();
        setPublicHistories(data);
      } catch (error) {
        console.error('Error fetching public Wrapped histories:', error);
      }
    };

    fetchPublicHistories();
  }, []);

  return (
    <div>
      <h1>Public Wrapped History</h1>
      {publicHistories.map((history) => (
        <div key={history.id}>
          <h2>{history.title}</h2>
          <img src={history.image} alt={history.title} />
          {/* Display artists */}
          <ul>
            {history.artists.map((artist, idx) => (
              <li key={idx}>{artist}</li>
            ))}
          </ul>
          {/* Display tracks */}
          <ul>
            {history.tracks.map((track, idx) => (
              <li key={idx}>{track}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
};

export default PublicWrapped;

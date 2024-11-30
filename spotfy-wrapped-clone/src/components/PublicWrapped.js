// PublicWrapped.js

import React, { useEffect, useState } from 'react';

const PublicWrapped = () => {
  const [publicHistories, setPublicHistories] = useState([]);

  useEffect(() => {
    const fetchPublicHistories = async () => {
      try {
        const response = await fetch('/api/public_histories/');
        const data = await response.json();
        setPublicHistories(data);
      } catch (error) {
        console.error(error);
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
          {/* Display artists and tracks */}
          <ul>
            {history.artists.map((artist, idx) => (
              <li key={idx}>{artist}</li>
            ))}
          </ul>
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

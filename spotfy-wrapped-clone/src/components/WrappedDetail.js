import React, { useState, useEffect, useRef } from "react";
import { useLocation, useNavigate } from "react-router-dom";

function WrappedDetail() {
  const location = useLocation();
  const navigate = useNavigate();
  const artists = location.state?.fullData; // Retrieve artist data from navigation state
  const [currentIndex, setCurrentIndex] = useState(0);
  const audioRef = useRef(null); // Reference to audio element
  const [audioReady, setAudioReady] = useState(false); // Flag to ensure user interaction for autoplay

  useEffect(() => {
    if (!artists) {
      navigate("/home"); // Redirect to home if no artist data is available
    }
  }, [artists, navigate]);

  useEffect(() => {
    // Play the audio for the current artist when it has loaded
    if (audioReady && audioRef.current) {
      const playAudio = async () => {
        try {
          audioRef.current.load(); // Reload the audio source
          await audioRef.current.play(); // Play audio only after it is ready
        } catch (err) {
          console.error("Error playing audio:", err);
        }
      };
      playAudio();
    }
  }, [currentIndex, audioReady]); // Trigger when the current artist or audioReady changes

  const handlePlayAudio = () => {
    // Ensure the user interaction allows autoplay
    setAudioReady(true);
    if (audioRef.current) {
      audioRef.current.play();
    }
  };

  const handleNext = () => {
    setCurrentIndex((prevIndex) => (prevIndex + 1) % artists.length);
  };

  const handlePrev = () => {
    setCurrentIndex((prevIndex) =>
      prevIndex === 0 ? artists.length - 1 : prevIndex - 1
    );
  };

  if (!artists) {
    return <div>Loading...</div>; // Fallback if no artists are provided
  }

  const currentArtist = artists[currentIndex];

  return (
    <div
      className="flex flex-col items-center justify-center h-screen bg-spotifyBlack text-white"
      onClick={handlePlayAudio} // Ensure autoplay is enabled after a user click
    >
      <div className="w-full max-w-lg text-center">
        <img
          src={currentArtist.images[0]?.url || "https://via.placeholder.com/300"}
          alt={currentArtist.name}
          className="rounded-lg shadow-md"
        />
        <h2 className="mt-4 text-3xl font-bold text-spotifyGreen">
          {currentArtist.name}
        </h2>
        <p className="mt-2 text-gray-400">{currentArtist.description || "No description available."}</p>
        {/* Hidden audio element for background playback */}
        <audio ref={audioRef}>
          <source src={currentArtist.song_preview} type="audio/mpeg" />
          Your browser does not support the audio element.
        </audio>
      </div>
      <div className="flex mt-6 space-x-4">
        <button
          onClick={handlePrev}
          className="px-4 py-2 bg-spotifyGreen text-black font-bold rounded hover:bg-spotifyGreenHover transition"
        >
          Previous
        </button>
        <button
          onClick={handleNext}
          className="px-4 py-2 bg-spotifyGreen text-black font-bold rounded hover:bg-spotifyGreenHover transition"
        >
          Next
        </button>
      </div>
      <button
        onClick={() => navigate("/home")}
        className="mt-8 px-4 py-2 bg-spotifyGreen text-black font-bold rounded hover:bg-spotifyGreenHover transition"
      >
        Back to Home
      </button>
    </div>
  );
}

export default WrappedDetail;

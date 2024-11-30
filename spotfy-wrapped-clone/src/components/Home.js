import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import SpotifyWrappedCarousel from "./SpotifyWrappedCarousel";

function Home() {
  const [profileData, setProfileData] = useState(null);
  const [slides, setSlides] = useState([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem("theme") === "dark");
  const navigate = useNavigate();

  // Apply dark or light theme based on `isDarkMode`
  useEffect(() => {
    document.body.classList.toggle("dark", isDarkMode);
    document.body.classList.toggle("light", !isDarkMode);
    localStorage.setItem("theme", isDarkMode ? "dark" : "light");
  }, [isDarkMode]);

  useEffect(() => {
    const fetchProfileAndHistory = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}profile/`, {
          method: "GET",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
          },
        });

        if (response.ok) {
          const data = await response.json();
          setProfileData(data);

          // Fetch wrapped history after fetching profile
          const historyResponse = await fetch(`${process.env.REACT_APP_API_BASE_URL}spotify/wrapped-history/`, {
            method: "GET",
            headers: {
              Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
            },
          });

          if (historyResponse.ok) {
            const historyData = await historyResponse.json();
            setSlides(historyData); // Populate carousel with wrapped history
          } else {
            console.error("Failed to fetch Wrapped history.");
          }
        } else {
          alert("Failed to fetch profile data. Please log in again.");
          navigate("/login");
        }
      } catch (error) {
        console.error("Error fetching profile data or Wrapped history:", error);
        navigate("/login");
      }
    };

    fetchProfileAndHistory();
  }, [navigate]);

  const generateWrapped = async (term) => {
    if (!profileData?.spotify_linked) {
      alert("Please link your Spotify account first.");
      return;
    }

    try {
      const response = await fetch(
        `${process.env.REACT_APP_API_BASE_URL}spotify/wrapped-data/${term}/`,
        {
          method: "GET",
          headers: {
            Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        console.log("Spotify Wrapped Data:", data);

        const imageUrl = data[0]?.images[0]?.url || "https://via.placeholder.com/300";

        const newSlide = {
          id: `wrapped-${Date.now()}`, // Unique ID for this Wrapped summary
          title: `${term.charAt(0).toUpperCase() + term.slice(1)}-Term Wrapped`,
          image: imageUrl, // Use the image URL from the data
          fullData: data, // Pass all artist details for the next page
          tracks: data.tracks,
          artists: data.artists // Ensure artists are passed here
        };

        setSlides((prevSlides) => [...prevSlides, newSlide]);
        alert(`Generated ${term}-term Wrapped successfully!`);
      } else {
        alert("Failed to generate Wrapped.");
      }
    } catch (error) {
      console.error("Error generating Wrapped:", error);
      alert("An error occurred while generating Wrapped.");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    navigate("/login");
  };

  const handleLinkSpotify = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}spotify/auth-url/`);
      if (response.ok) {
        const data = await response.json();
        window.location.href = data.url;
      } else {
        alert("Failed to fetch Spotify authorization URL.");
      }
    } catch (error) {
      console.error("Error fetching Spotify authorization URL:", error);
      alert("An error occurred while linking Spotify.");
    }
  };
  
  const handleDeleteAccount = async () => {
    const token = localStorage.getItem("accessToken");  // Assuming the token is stored here
  
    if (!token) {
      alert("You must be logged in to delete your account.");
      return;
    }
  
    try {
      const response = await fetch('http://127.0.0.1:8000/api/users/delete/', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,  // Include the token
          'Content-Type': 'application/json',
        },
      });
  
      if (response.ok) {
        alert("Account deleted successfully.");
        localStorage.removeItem("accessToken");  // Clear token
        window.location.href = '/login';  // Redirect to login page
      } else {
        alert("Failed to delete account.");
      }
    } catch (error) {
      console.error("Error deleting account:", error);
      alert("An error occurred while deleting your account.");
    }
  };

  const toggleDarkMode = () => {
    setIsDarkMode((prevMode) => !prevMode);
  };

  return (
    <div className="flex h-screen w-screen bg-spotifyBlack text-white overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-spotifyDark flex-shrink-0 p-4 flex flex-col">
        <div>
          <h2 className="text-xl font-bold text-spotifyGreen mb-6">
            {profileData ? `${profileData.username}'s Spotify Wrapped` : "Spotify Wrapped"}
          </h2>
          <button
            className="w-full py-2 px-4 mb-4 bg-spotifyGreen text-black font-bold rounded hover:bg-spotifyGreenHover transition"
            onClick={() => generateWrapped("short")}
          >
            Short-Term Wrapped
          </button>
          <button
            className="w-full py-2 px-4 mb-4 bg-spotifyGreen text-black font-bold rounded hover:bg-spotifyGreenHover transition"
            onClick={() => generateWrapped("medium")}
          >
            Medium-Term Wrapped
          </button>
          <button
            className="w-full py-2 px-4 mb-4 bg-spotifyGreen text-black font-bold rounded hover:bg-spotifyGreenHover transition"
            onClick={() => generateWrapped("long")}
          >
            Long-Term Wrapped
          </button>
          <button
            className="w-full py-2 px-4 mb-4 bg-spotifyGreen text-black font-bold rounded hover:bg-spotifyGreenHover transition"
            onClick={() => generateWrapped("christmas")}
          >
            Christmas Wrapped
          </button>
          <button
            className="w-full py-2 px-4 mb-4 bg-spotifyGreen text-black font-bold rounded hover:bg-spotifyGreenHover transition"
            onClick={() => generateWrapped("halloween")}
          >
            Halloween Wrapped
          </button>
          <div className="flex-grow mt-4">
            <button
              className="w-full py-2 px-4 bg-spotifyGreen text-black font-bold rounded hover:bg-spotifyRedHover transition"
              onClick={() => navigate("/game")}
            >
              Play a Game
            </button>
          </div>
          <div className="mt-4">
            <button
              className="w-full py-2 px-4 bg-spotifyGreen text-black font-bold rounded hover:bg-spotifyYellowHover transition"
              onClick={() => navigate("/contact")}
            >
              Contact Developers
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <nav className="bg-spotifyDark p-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-spotifyGreen">
            {profileData ? `Welcome, ${profileData.username}` : "Your Wrapped Dashboard"}
          </h1>
          <div className="relative">
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="px-4 py-2 bg-spotifyGreen text-black font-bold rounded hover:bg-spotifyGreenHover transition"
            >
              Profile
            </button>
            {isDropdownOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-spotifyDark rounded shadow-lg">
                <button
                  className="w-full px-4 py-2 text-white hover:bg-spotifyGreen hover:text-black transition"
                  onClick={handleLogout}
                >
                  Log Out
                </button>
                <button
                  className="w-full px-4 py-2 text-white hover:bg-spotifyGreen hover:text-black transition"
                  onClick={handleLinkSpotify}
                >
                  Link Spotify
                </button>
                <button
                  className="w-full px-4 py-2 text-white hover:bg-spotifyGreen hover:text-black transition"
                  onClick={handleDeleteAccount}
                >
                  Delete Account
                </button>
                <button
                  className="w-full px-4 py-2 text-white hover:bg-spotifyGreen hover:text-black transition"
                  onClick={toggleDarkMode}
                >
                  Toggle {isDarkMode ? "Light" : "Dark"} Mode
                </button>
              </div>
            )}
          </div>
        </nav>

        {/* Spotify Wrapped Carousel */}
        <div className="flex-1 p-8 overflow-y-auto">
          <SpotifyWrappedCarousel
            slides={slides}
            onSlideClick={(slide) => {
              navigate(`/wrapped-detail/${slide.id}`, { state: slide });
            }}
          />
        </div>
      </div>
    </div>
  );
}

export default Home;

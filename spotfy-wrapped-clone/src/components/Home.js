import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import SpotifyWrappedCarousel from "./SpotifyWrappedCarousel";



/**
 * Home Component
 *
 * This component serves as the main dashboard for the application.
 * It displays the user's Spotify Wrapped history, provides options to generate new Wrapped summaries
 * (short, medium, long, Christmas, Halloween), and includes features like dark mode toggle and user account management.
 *
 * Features:
 * - Fetches user profile and Wrapped history.
 * - Allows generating new Wrapped summaries based on time ranges or themes.
 * - Supports dark/light mode toggling.
 * - Provides options to link Spotify, logout, or delete the user account.
 * - Displays a carousel of Spotify Wrapped summaries.
 */
function Home() {
  const [profileData, setProfileData] = useState(null); // Stores user profile data
  const [slides, setSlides] = useState([]); // Stores slides for the Wrapped carousel
  const [isDropdownOpen, setIsDropdownOpen] = useState(false); // Toggles profile dropdown
  const [isDarkMode, setIsDarkMode] = useState(localStorage.getItem("theme") === "dark"); // Tracks dark mode state
  const navigate = useNavigate();

  // Apply dark or light theme based on `isDarkMode`
  useEffect(() => {
    document.body.classList.toggle("dark", isDarkMode);
    document.body.classList.toggle("light", !isDarkMode);
    localStorage.setItem("theme", isDarkMode ? "dark" : "light");
  }, [isDarkMode]);
  
  const [dark, setDark] = React.useState(false);

  /**
  * Toggles the application's theme between dark and light modes.
  */
  const darkModeHandler = () => {
      setDark(!dark);
      setIsDarkMode((prevMode) => !prevMode);
      document.body.classList.toggle("dark");
  }

  /**
   * Fetches the user's profile data and Spotify Wrapped history on component mount.
   * Redirects to the login page if fetching profile data fails.
   */
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

          // Fetch Wrapped history after fetching profile
          const historyResponse = await fetch(`${process.env.REACT_APP_API_BASE_URL}spotify/wrapped-history/`, {
            method: "GET",
            headers: {
              Authorization: `Bearer ${localStorage.getItem("accessToken")}`,
            },
          });

          if (historyResponse.ok) {
            const historyData = await historyResponse.json();
            setSlides(historyData); // Populate carousel with Wrapped history
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

  /**
   * Generates a new Spotify Wrapped summary for the specified term.
   *
   * @param {string} term - The term for Wrapped (e.g., "short", "medium", "long", "christmas", "halloween").
   */
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
          artists: data.artists, // Ensure artists are passed here
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

  /**
   * Logs the user out by clearing stored tokens and navigating to the login page.
   */
  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    navigate("/login");
  };

  /**
   * Initiates the Spotify account linking process by fetching the authorization URL.
   */
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

  /**
   * Deletes the user's account by sending a DELETE request to the API.
   */
  const handleDeleteAccount = async () => {
    const token = localStorage.getItem("accessToken");

    if (!token) {
      alert("You must be logged in to delete your account.");
      return;
    }

    try {
      const response = await fetch(`${process.env.REACT_APP_API_BASE_URL}users/delete/`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
      });

      if (response.ok) {
        alert("Account deleted successfully.");
        localStorage.removeItem("accessToken");
        navigate("/login");
      } else {
        alert("Failed to delete account.");
      }
    } catch (error) {
      console.error("Error deleting account:", error);
      alert("An error occurred while deleting your account.");
    }
  };

  return (
    <div className="flex h-screen w-screen bg-spotifyWhite dark:bg-spotifyBlack text-white dark:text-spotifyBlack overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-spotifyLight dark:bg-spotifyDark flex-shrink-0 p-4 flex flex-col">
        <div>
          <h2 className="text-xl font-bold text-spotifyGreen mb-6">
            {profileData ? `${profileData.username}'s Spotify Wrapped` : "Spotify Wrapped"}
          </h2>
          <button
            className="w-full py-2 px-4 mb-4 bg-spotifyGreen text-white dark:text-black font-bold rounded hover:bg-spotifyGreenHover transition hover:scale-105"
            onClick={() => generateWrapped("short")}
          >
            Short-Term Wrapped
          </button>
          <button
            className="w-full py-2 px-4 mb-4 bg-spotifyGreen text-white dark:text-black font-bold rounded hover:bg-spotifyGreenHover transition hover:scale-105"
            onClick={() => generateWrapped("medium")}
          >
            Medium-Term Wrapped
          </button>
          <button
            className="w-full py-2 px-4 mb-4 bg-spotifyGreen text-white dark:text-black font-bold rounded hover:bg-spotifyGreenHover transition hover:scale-105"
            onClick={() => generateWrapped("long")}
          >
            Long-Term Wrapped
          </button>
          <button
            className="w-full py-2 px-4 mb-4 bg-spotifyGreen text-white dark:text-black font-bold rounded hover:bg-spotifyGreenHover transition hover:scale-105"
            onClick={() => generateWrapped("christmas")}
          >
            Christmas Wrapped
          </button>
          <button
            className="w-full py-2 px-4 mb-4 bg-spotifyGreen text-white dark:text-black font-bold rounded hover:bg-spotifyGreenHover transition hover:scale-105"
            onClick={() => generateWrapped("halloween")}
          >
            Halloween Wrapped
          </button>
          <div className="flex-grow mt-4">
            <button
              className="w-full py-2 px-4 bg-spotifyGreen text-white dark:text-black font-bold rounded hover:bg-spotifyRedHover transition hover:scale-105"
              onClick={() => navigate("/game")}
            >
              Play a Game
            </button>
          </div>
          <div className="mt-4">
            <button
              className="w-full py-2 px-4 bg-spotifyGreen text-white dark:text-black font-bold rounded hover:bg-spotifyYellowHover transition hover:scale-105"
              onClick={() =>
                (window.location.href = "https://jessezhang0.wixsite.com/2340team/about")
              }
            >
              Contact Developers
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <nav className="bg-spotifyLight dark:bg-spotifyDark p-4 flex justify-between items-center">
          <h1 className="text-xl font-bold text-spotifyGreen">
            {profileData ? `Welcome, ${profileData.username}` : "Your Wrapped Dashboard"}
          </h1>
          <div className="relative">
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="px-4 py-2 bg-spotifyGreen text-white dark:text-black font-bold rounded hover:bg-spotifyGreenHover transition hover:scale-105"
            >
              Profile
            </button>
            {isDropdownOpen && (
              <div className="absolute right-0 mt-2 w-48 bg-spotifyLight dark:bg-spotifyDark rounded shadow-lg z-10 border-2">
                <button
                  className="w-full px-4 py-2 text-spotifyGreen dark:text-white hover:bg-spotifyGreen hover:text-white transition dark:hover:text-black transition hover:scale-105"
                  onClick={handleLogout}
                >
                  Log Out
                </button>
                <button
                  className="w-full px-4 py-2 text-spotifyGreen dark:text-white hover:bg-spotifyGreen hover:text-white transition dark:hover:text-black transition hover:scale-105"
                  onClick={handleLinkSpotify}
                >
                  Link Spotify
                </button>
                <button
                  className="w-full px-4 py-2 text-spotifyGreen dark:text-white hover:bg-spotifyGreen hover:text-white transition dark:hover:text-black transition hover:scale-105"
                  onClick={handleDeleteAccount}
                >
                  Delete Account
                </button>
                <button
                  className="w-full px-4 py-2 text-spotifyGreen dark:text-white hover:bg-spotifyGreen hover:text-white transition dark:hover:text-black transition hover:scale-105"
                  onClick={darkModeHandler}
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

import React from "react";
import Carousel from "react-multi-carousel";
import "react-multi-carousel/lib/styles.css";

/**
 * SpotifyWrappedCarousel Component
 *
 * This component renders a responsive carousel displaying Spotify Wrapped summaries.
 * It allows users to interact with individual slides by clicking on them, triggering a callback.
 *
 * Props:
 * - slides: An array of objects representing the carousel slides. Each object includes:
 *   - id: A unique identifier for the slide.
 *   - image: A URL for the slide's image.
 *   - title: A string representing the slide's title.
 * - onSlideClick: A callback function triggered when a slide is clicked, receiving the slide object as an argument.
 *
 * Features:
 * - Responsive design that adjusts the number of visible slides based on screen size.
 * - Displays slide images and titles.
 * - Allows interaction with individual slides.
 */
function SpotifyWrappedCarousel({ slides, onSlideClick }) {
  const responsive = {
    desktop: { breakpoint: { max: 3000, min: 1024 }, items: 3 },
    tablet: { breakpoint: { max: 1024, min: 464 }, items: 2 },
    mobile: { breakpoint: { max: 464, min: 0 }, items: 1 },
  };

  return (
    <Carousel responsive={responsive}>
      {slides.map((slide) => (
        <div
          key={slide.id} // Use a unique key for each slide
          className="p-4 cursor-pointer"
          onClick={() => onSlideClick(slide)}
        >
          <img
            src={slide.image}
            alt={slide.title}
            className="rounded-lg shadow-md"
          />
          <h3 className="mt-2 text-center font-bold text-spotifyGreen">
            {slide.title}
          </h3>
        </div>
      ))}
    </Carousel>
  );
}

export default SpotifyWrappedCarousel;

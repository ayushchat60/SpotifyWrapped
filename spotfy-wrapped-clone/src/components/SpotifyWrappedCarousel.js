import React from "react";
import Carousel from "react-multi-carousel";
import "react-multi-carousel/lib/styles.css";

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
          key={slide.id}
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

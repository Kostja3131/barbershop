
// JavaScript for Continuous Infinite Testimonials Carousel
document.addEventListener('DOMContentLoaded', () => {
    const track = document.querySelector('.carousel-track');
    const slides = Array.from(track.children);
    let currentIndex = 0;

    // Clone slides for infinite effect
    const cloneCount = slides.length;
    slides.forEach(slide => {
        const clone = slide.cloneNode(true);
        track.appendChild(clone);
    });

    const updateCarousel = () => {
        const slideWidth = slides[0].getBoundingClientRect().width;
        track.style.transform = `translateX(-${currentIndex * slideWidth}px)`;

        // Infinite loop logic
        if (currentIndex >= cloneCount) {
            setTimeout(() => {
                track.style.transition = 'none';
                currentIndex = 0;
                track.style.transform = `translateX(0px)`;
                setTimeout(() => {
                    track.style.transition = 'transform 0.5s ease-in-out';
                }, 50);
            }, 500);
        }
    };

    // Continuous auto-scroll
    const autoScroll = () => {
        currentIndex++;
        track.style.transition = 'transform 0.5s ease-in-out';
        updateCarousel();
    };

    // Start auto-scrolling every 3 seconds
    setInterval(autoScroll, 3000);

    // Adjust on window resize
    window.addEventListener('resize', updateCarousel);
});
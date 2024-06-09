document.addEventListener('DOMContentLoaded', () => {
    let startX;
    let currentTranslate = 0;
    const carousel = document.querySelector('.carousel');

    carousel.addEventListener('touchstart', (e) => {
        startX = e.touches[0].clientX;
    });

    carousel.addEventListener('touchmove', (e) => {
        const moveX = e.touches[0].clientX;
        const diff = startX - moveX;
        if (Math.abs(diff) > 50) {
            if (diff > 0) {
                // swipe left
                nextSlide();
            } else {
                // swipe right
                prevSlide();
            }
            startX = moveX;
        }
    });

    function nextSlide() {
        if (currentTranslate > -(carousel.children.length - 1) * 100) {
            currentTranslate -= 100;
            updateCarousel();
        }
    }

    function prevSlide() {
        if (currentTranslate < 0) {
            currentTranslate += 100;
            updateCarousel();
        }
    }

    function updateCarousel() {
        carousel.style.transform = `translateX(${currentTranslate}%)`;
    }
});

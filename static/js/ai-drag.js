
document.addEventListener("DOMContentLoaded", function () {
    const button = document.querySelector(".ai-floating-button");
    if (!button) return;

    let startX = 0;
    let startY = 0;
    let initialLeft = 0;
    let initialTop = 0;
    let dragging = false;
    let moved = false;
    let preventNextClick = false;

    button.style.touchAction = "none";
    button.style.userSelect = "none";
    button.style.webkitUserSelect = "none";
    button.style.cursor = "grab";

    button.addEventListener("pointerdown", function (event) {
        if (event.pointerType === "mouse" && event.button !== 0) return;

        const rect = button.getBoundingClientRect();

        startX = event.clientX;
        startY = event.clientY;
        initialLeft = rect.left;
        initialTop = rect.top;

        dragging = true;
        moved = false;

        button.setPointerCapture(event.pointerId);
    });

    button.addEventListener("pointermove", function (event) {
        if (!dragging) return;

        const dx = event.clientX - startX;
        const dy = event.clientY - startY;

        if (Math.abs(dx) > 5 || Math.abs(dy) > 5) {
            moved = true;
        }

        if (!moved) return;

        const left = Math.max(
            0,
            Math.min(initialLeft + dx, window.innerWidth - button.offsetWidth)
        );

        const top = Math.max(
            0,
            Math.min(initialTop + dy, window.innerHeight - button.offsetHeight)
        );

        button.style.left = left + "px";
        button.style.top = top + "px";
        button.style.right = "auto";
        button.style.bottom = "auto";

        button.style.cursor = "grabbing";
    });

    function stopDragging() {
        if (!dragging) return;

        if (moved) {
            preventNextClick = true;
        }

        dragging = false;
        button.style.cursor = "grab";
    }

    button.addEventListener("pointerup", stopDragging);
    button.addEventListener("pointercancel", stopDragging);

    button.addEventListener("dragstart", function (event) {
        event.preventDefault();
    });

    button.addEventListener("click", function (event) {
        if (preventNextClick) {
            event.preventDefault();
            preventNextClick = false;
        }
    });
});

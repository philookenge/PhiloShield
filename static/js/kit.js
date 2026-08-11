const kitCheckboxes = document.querySelectorAll(
    '.status-card input[type="checkbox"]'
);

kitCheckboxes.forEach(function (checkbox, index) {
    const savedValue = localStorage.getItem("kitItem" + index);

    if (savedValue === "checked") {
        checkbox.checked = true;
    }

    checkbox.addEventListener("change", function () {
        if (checkbox.checked) {
            localStorage.setItem("kitItem" + index, "checked");
        } else {
            localStorage.removeItem("kitItem" + index);
        }
    });
});

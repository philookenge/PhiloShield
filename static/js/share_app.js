const shareAppButton = document.getElementById("shareAppButton");

shareAppButton.addEventListener("click", async () => {

    const shareData = {
        title: "PhiloShield",
        text: "Check out PhiloShield — an emergency safety and preparedness app.",
        url: window.location.origin
    };

    if (navigator.share) {
        try {
            await navigator.share(shareData);
        } catch (error) {
            console.log("Sharing cancelled.");
        }
    } else {
        await navigator.clipboard.writeText(window.location.origin);
        alert("PhiloShield link copied!");
    }

});

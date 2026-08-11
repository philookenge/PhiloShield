const flashlightButton = document.getElementById("flashlightButton");
const strobeButton = document.getElementById("strobeButton");
const alarmButton = document.getElementById("alarmButton");
const stopButton = document.getElementById("stopButton");
const status = document.getElementById("flashlightStatus");

let strobeInterval = null;
let alarmInterval = null;

flashlightButton.addEventListener("click", () => {
    document.body.style.background = "white";
    document.body.style.color = "black";
    status.innerHTML = "🔦 Bright screen activated.";
});

strobeButton.addEventListener("click", () => {

    if (strobeInterval) return;

    let on = false;

    strobeInterval = setInterval(() => {

        document.body.style.background =
            on ? "white" : "red";

        document.body.style.color =
            on ? "black" : "white";

        on = !on;

    }, 400);

    status.innerHTML = "🚨 SOS strobe is running.";
});

const alarmAudio = new Audio("/static/audio/Alarm.mp3");
alarmAudio.loop = true;

alarmButton.addEventListener("click", function () {
    alarmAudio.currentTime = 0;

    alarmAudio.play()
        .then(function () {
            status.innerHTML = "🔊 Emergency alarm playing.";
        })
        .catch(function (error) {
            console.error(error);

            status.innerHTML =
                "❌ Alarm could not play. Check the sound file name.";
        });
});


stopButton.addEventListener("click", () => {

    clearInterval(strobeInterval);
    clearInterval(alarmInterval);
    alarmAudio.pause();
    alarmAudio.currentTime = 0;


    strobeInterval = null;
    alarmInterval = null;

    document.body.style.background = "#eef4f9";
    document.body.style.color = "#222";

    status.innerHTML = "✅ Emergency tools stopped.";

});

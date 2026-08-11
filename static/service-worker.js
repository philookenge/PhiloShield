const CACHE_NAME = "philoshield-v3";

const FILES_TO_CACHE = [
    "/",
    "/offline",
    "/firstaid",
    "/kit",
    "/family",
    "/contacts",
    "/medicalid",
    "/share",
    "/flashlight",
    "/sos",

    "/static/css/style.css",

    "/static/js/firstaid.js",
    "/static/js/kit.js",
    "/static/js/family.js",
    "/static/js/contacts.js",
    "/static/js/medicalid.js",
    "/static/js/share.js",
    "/static/js/flashlight.js",
    "/static/js/sos.js",

    "/static/audio/Alarm.mp3"
];


self.addEventListener("install", function (event) {
    event.waitUntil(
        caches.open(CACHE_NAME).then(function (cache) {
            return cache.addAll(FILES_TO_CACHE);
        })
    );
});

self.addEventListener("fetch", function (event) {
    event.respondWith(
        caches.match(event.request)
            .then(function (cachedResponse) {

                if (cachedResponse) {
                    return cachedResponse;
                }

                return fetch(event.request)
                    .catch(function () {

                        if (event.request.mode === "navigate") {
                            return caches.match("/offline");
                        }

                        throw new Error("Offline resource unavailable.");
                    });
            })
    );
});

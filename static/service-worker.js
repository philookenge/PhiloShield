const CACHE_NAME = "philoshield-v5";

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

    "/static/manifest.json",
    "/static/icons/icon-192.png",
    "/static/icons/icon-512.png",

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
    self.skipWaiting();

    event.waitUntil(
        caches.open(CACHE_NAME).then(function (cache) {
            return cache.addAll(FILES_TO_CACHE);
        })
    );
});

self.addEventListener("activate", function (event) {
    event.waitUntil(
        caches.keys().then(function (cacheNames) {
            return Promise.all(
                cacheNames.map(function (cacheName) {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(function () {
            return self.clients.claim();
        })
    );
});


self.addEventListener("fetch", function (event) {

    // For pages: try the newest online version first.
    if (event.request.mode === "navigate") {
        event.respondWith(
            fetch(event.request)
                .then(function (response) {
                    return response;
                })
                .catch(function () {
                    return caches.match(event.request)
                        .then(function (cachedResponse) {
                            return cachedResponse || caches.match("/offline");
                        });
                })
        );

        return;
    }

    // For CSS, JS, icons, audio, etc.
    event.respondWith(
        caches.match(event.request)
            .then(function (cachedResponse) {
                return cachedResponse || fetch(event.request);
            })
    );
});

self.addEventListener("push", function (event) {
    let data = {
        title: "PhiloShield Emergency Alert",
        body: "You have a new emergency notification."
    };

    if (event.data) {
        try {
            data = event.data.json();
        } catch (error) {
            data.body = event.data.text();
        }
    }

    event.waitUntil(
        self.registration.showNotification(data.title, {
            body: data.body,
            icon: "/static/icons/icon-192.png",
            badge: "/static/icons/icon-192.png"
        })
    );
});

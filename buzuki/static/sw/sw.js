const web_cache = "web-app-cache-v1.0";
const filesToCache = [
  "/",
  "/static/dist/buzuki.min.js",
  "/static/dist/buzuki.min.css",
  "/static/favicon/android-chrome-192x192.png",
  "/static/favicon/android-chrome-512x512.png",
  "/static/favicon/apple-touch-icon.png",
  "/static/favicon/favicon.ico",
  "/static/favicon/favicon-16x16.png",
  "/static/favicon/favicon-32x32.png",
  "/static/favicon/site.webmanifest"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(web_cache).then(cache => {
      return cache.addAll(filesToCache);
    })
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches
      .match(event.request)
      .then(response => {
        if (response) {
          return response;
        } else {
          return fetch(event.request);
        }
      })
      .catch(error => {})
  );
});

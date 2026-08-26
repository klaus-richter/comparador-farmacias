// Service Worker para instalación PWA Standalone Fullscreen
const CACHE_NAME = 'comparador-farmacias-v2';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(clients.claim());
});

self.addEventListener('fetch', (event) => {
  // Network first con fallback normal
  event.respondWith(
    fetch(event.request).catch(() => caches.match(event.request))
  );
});

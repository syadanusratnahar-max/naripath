/* NariPath service worker: keeps the app usable offline.
   Pages: network first, fall back to the saved copy. Fonts and icons: saved copy first.
   Only same-origin files are handled; NariPath makes no third-party requests. */
const CACHE = "naripath-v6";
const FONTS = [
  "hind-siliguri-bengali-400-normal", "hind-siliguri-bengali-500-normal", "hind-siliguri-bengali-600-normal", "hind-siliguri-bengali-700-normal",
  "hind-siliguri-latin-400-normal", "hind-siliguri-latin-500-normal", "hind-siliguri-latin-600-normal", "hind-siliguri-latin-700-normal",
  "tiro-bangla-bengali-400-normal", "tiro-bangla-latin-400-normal"
].map(f => "./fonts/" + f + ".woff2");
const CORE = ["./", "./index.html", "./manifest.webmanifest", "./icons/icon-192.png", "./icons/icon-512.png", "./icons/apple-touch-icon.png"].concat(FONTS);

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  const isPage = req.mode === "navigate" || url.pathname.endsWith(".html");
  if (isPage) {
    e.respondWith(fetch(req).then(res => {
      if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put("./index.html", copy)); }
      return res;
    }).catch(() => caches.match("./index.html")));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => {
    if (res && res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return res;
  })));
});

// Analytics Tracking Script

// API endpoint of analytics-service
//const endpoint = "http://localhost:8085/track"; // docker
//const endpoint = "http://192.168.49.2:30805/track";
//const endpoint = "http://127.0.0.1:64782/track"; // minikube service analytics-service --url
const endpoint = "/track"; // relative path

// Generate or retrieve unique session ID
function getSessionId() {
  let sessionId = localStorage.getItem("session_id");
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem("session_id", sessionId);
  }
  return sessionId;
}

// Send event to backend
function sendEvent(eventType, pageUrl, extraData = {}) {
  const payload = {
    event_type: eventType,
    page_url: pageUrl,
    user_agent: navigator.userAgent,
    session_id: getSessionId(),
    ...extraData
  };

  fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  }).catch(err => console.error("Failed to log event:", err));
}

// Run tracking setup after DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  
  // Track page view immediately
  sendEvent("page_view", window.location.href);

  // Track clicks
  document.addEventListener("click", e => {
    sendEvent("click", window.location.href, {
      tag: e.target.tagName,
      class: e.target.className,
      id: e.target.id
    });
  });

  // Track scroll
  document.addEventListener("scroll", () => {
    const scrollPercent = (window.scrollY / (document.body.scrollHeight - window.innerHeight)) * 100;
    sendEvent("scroll", window.location.href, { scroll_percent: Math.round(scrollPercent) });
  });

  // Track session time on page unload
  const sessionStart = Date.now();
  window.addEventListener("beforeunload", () => {
    const sessionTime = Math.round((Date.now() - sessionStart) / 1000);
    sendEvent("session_time", window.location.href, { duration_seconds: sessionTime });
  });

});

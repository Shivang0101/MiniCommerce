import React, { useState, useEffect } from "react";

export default function RateLimitModal({ isOpen, cooldownSeconds, onClose }) {
  const [secondsLeft, setSecondsLeft] = useState(cooldownSeconds);

  useEffect(() => {
    setSecondsLeft(cooldownSeconds);
    if (!isOpen || cooldownSeconds <= 0) return;

    const timer = setInterval(() => {
      setSecondsLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          onClose();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isOpen, cooldownSeconds]);

  if (!isOpen) return null;

  return (
    <div className="modal-backdrop">
      <div className="modal-content" style={{ maxWidth: "420px", textAlign: "center", borderTop: "4px solid #ef4444" }}>
        <div style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>⚡</div>
        <h2 style={{ color: "#ef4444", marginBottom: "0.5rem", fontSize: "1.25rem", fontWeight: "700" }}>
          Rate Limit Exceeded (HTTP 429)
        </h2>
        <p style={{ color: "#94a3b8", fontSize: "0.9rem", marginBottom: "1.5rem", lineHeight: "1.5" }}>
          Our Redis sliding-window rate limiter has paused your requests to protect API performance and database integrity.
        </p>

        <div style={{
          background: "rgba(239, 68, 68, 0.1)",
          border: "1px solid rgba(239, 68, 68, 0.3)",
          borderRadius: "12px",
          padding: "1rem",
          marginBottom: "1.5rem"
        }}>
          <div style={{ fontSize: "0.8rem", color: "#f87171", textTransform: "uppercase", letterSpacing: "1px", fontWeight: "600" }}>
            Cooldown Active
          </div>
          <div style={{ fontSize: "2.5rem", fontWeight: "800", color: "#ef4444", fontFamily: "monospace" }}>
            {secondsLeft}s
          </div>
        </div>

        <button
          onClick={onClose}
          className="btn btn-secondary"
          style={{ width: "100%" }}
        >
          Dismiss & Wait
        </button>
      </div>
    </div>
  );
}

import { useState } from "react";
import { maloneApi } from "../../lib/maloneApi";

export default function ChatPanel({ onResponse }) {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(e) {
    e.preventDefault();

    const nextMessage = message.trim();
    if (!nextMessage) {
      setError("Please enter a request for Malone.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const data = await maloneApi.chat(nextMessage);
      onResponse?.(data);
      setMessage("");
    } catch (err) {
      const nextError =
        err instanceof Error && err.message
          ? err.message
          : "Malone request failed";
      setError(nextError);
      onResponse?.(null);
    } finally {
      setLoading(false);
    }
  }

  function onKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!loading) {
        void onSubmit(e);
      }
    }
  }

  return (
    <div className="card">
      <h3>Ask Malone</h3>

      <form className="form-card" onSubmit={onSubmit}>
        <label htmlFor="malone-message">
          Message
        </label>

        <textarea
          id="malone-message"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={onKeyDown}
          placeholder="Ask Malone about schedules, summaries, current information, or a supported system task."
          rows={4}
          disabled={loading}
        />

        <div className="info-text">
          Press Enter to send. Press Shift+Enter for a new line.
        </div>

        <button className="primary-button" type="submit" disabled={loading}>
          {loading ? "Running..." : "Send"}
        </button>
      </form>

      {error ? <div className="error-text">{error}</div> : null}
    </div>
  );
}
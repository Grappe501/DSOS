import { useState } from "react";

export default function ChatPanel({ chat }) {
  const [message, setMessage] = useState("");
  const { loading, error, submitMessage, cancelRequest, setError } = chat;

  async function onSubmit(e) {
    e.preventDefault();

    const nextMessage = message.trim();
    if (!nextMessage) {
      setError("Please enter a request for Malone.");
      return;
    }

    const ok = await submitMessage(nextMessage);
    if (ok) {
      setMessage("");
    }
  }

  function onCancelRequest() {
    cancelRequest();
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

        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", alignItems: "center" }}>
          <button className="primary-button" type="submit" disabled={loading}>
            {loading ? "Running..." : "Send"}
          </button>
          <button
            className="secondary-button"
            type="button"
            onClick={onCancelRequest}
            disabled={!loading}
            title="Cancel the in-flight Malone request (HTTP abort)."
          >
            Cancel request
          </button>
        </div>
      </form>

      {error ? <div className="error-text">{error}</div> : null}
    </div>
  );
}

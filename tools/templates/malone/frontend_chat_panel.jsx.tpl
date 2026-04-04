import {{ useState }} from "react";
import {{ maloneApi }} from "../../lib/maloneApi";

export default function ChatPanel() {{
  const [message, setMessage] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function onSubmit(e) {{
    e.preventDefault();
    setLoading(true);
    setError("");
    try {{
      const data = await maloneApi.chat(message);
      setResponse(data);
    }} catch (err) {{
      setError(err.message || "Malone request failed");
    }} finally {{
      setLoading(false);
    }}
  }}

  return (
    <div className="card">
      <h3>Chat</h3>
      <form className="form-card" onSubmit={{onSubmit}}>
        <label>
          Message
          <input value={{message}} onChange={{(e) => setMessage(e.target.value)}} placeholder="Ask Malone to analyze, answer, or propose." />
        </label>
        <button className="primary-button" type="submit" disabled={{loading}}>
          {{loading ? "Running..." : "Send"}}
        </button>
      </form>

      {{error ? <div className="error-text">{{error}}</div> : null}}

      {{response ? (
        <pre className="inline-json">{{JSON.stringify(response, null, 2)}}</pre>
      ) : null}}
    </div>
  );
}}

import React, { useState } from "react";
import { classifyTask } from "../api";

export default function TaskInput({ onTaskConfirmed }) {
  const [text, setText] = useState("");
  const [mapping, setMapping] = useState(null);

  async function handleMap() {
    if (!text) return;
    try {
      const res = await classifyTask(text);
      setMapping(res);
      onTaskConfirmed(res.category);
    } catch (err) {
      console.error(err);
      alert("Could not map task: " + (err?.response?.data?.detail || err.message));
    }
  }

  return (
    <div className="panel">
      <div className="panel-title">Task description</div>
      <label className="field-label">What do you want the model to do?</label>
      <textarea
        className="textarea"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={'e.g., "Summarize legal contracts in plain English"'}
        rows={3}
      />
      <div className="button-row">
        <button className="primary-button" onClick={handleMap}>
          Map task → category
        </button>
        {mapping && (
          <div className="badge-subtle">
            Mapped to: {mapping.category} &nbsp;·&nbsp; score {mapping.score.toFixed(3)}
          </div>
        )}
      </div>
    </div>
  );
}

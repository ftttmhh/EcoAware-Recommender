import React, { useState } from "react";

export default function ConstraintsPanel({ onChange }) {
  const [minAcc, setMinAcc] = useState(70);
  const [maxLat, setMaxLat] = useState(500);
  const [priority, setPriority] = useState("balanced");

  function apply() {
    onChange({ minAcc, maxLat, priority });
  }

  return (
    <div className="panel">
      <div className="panel-title">Constraints & priorities</div>

      <div className="slider-row">
        <div className="slider-label">
          <span>Required accuracy</span>
          <span>{minAcc}%</span>
        </div>
        <input
          className="slider-input"
          type="range"
          min="50"
          max="100"
          value={minAcc}
          onChange={(e) => setMinAcc(+e.target.value)}
        />
      </div>

      <div className="slider-row">
        <div className="slider-label">
          <span>Latency tolerance (ms)</span>
          <span>{maxLat} ms</span>
        </div>
        <input
          className="slider-input"
          type="range"
          min="50"
          max="2000"
          step="10"
          value={maxLat}
          onChange={(e) => setMaxLat(+e.target.value)}
        />
      </div>

      <div style={{ marginTop: 6 }}>
        <span className="field-label">Sustainability priority</span>
        <div className="radio-group">
          <label className="radio-pill">
            <input
              type="radio"
              name="priority"
              value="accuracy-first"
              checked={priority === "accuracy-first"}
              onChange={(e) => setPriority(e.target.value)}
            />
            Accuracy-first
          </label>
          <label className="radio-pill">
            <input
              type="radio"
              name="priority"
              value="balanced"
              checked={priority === "balanced"}
              onChange={(e) => setPriority(e.target.value)}
            />
            Balanced
          </label>
          <label className="radio-pill">
            <input
              type="radio"
              name="priority"
              value="green-first"
              checked={priority === "green-first"}
              onChange={(e) => setPriority(e.target.value)}
            />
            Green-first
          </label>
        </div>
      </div>

      <div className="button-row">
        <button className="secondary-button" onClick={apply}>
          Apply filters
        </button>
      </div>
    </div>
  );
}

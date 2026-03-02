import React, { useState } from "react";
import TaskInput from "./components/TaskInput";
import ConstraintsPanel from "./components/ConstraintsPanel";
import ResultsTable from "./components/ResultsTable";
import TradeoffCharts from "./components/TradeoffCharts";
import { getRecommendations, setBaseline, getModelsForTask } from "./api";

function App() {
  const [taskCategory, setTaskCategory] = useState(null);
  const [filters, setFilters] = useState({ minAcc: 70, maxLat: 500, priority: "balanced" });
  const [recs, setRecs] = useState([]);
  const [recContext, setRecContext] = useState(null);
  const [baselineModel, setBaselineModel] = useState("");
  const [modelsForTask, setModelsForTask] = useState([]);

  async function handleRecommend() {
    if (!taskCategory) {
      alert("Map the task first (press Map task).");
      return;
    }
    try {
      const payload = {
        task: taskCategory,
        min_acc: filters.minAcc,
        max_lat: filters.maxLat,
        priority: filters.priority,
        topk: 5,
        baseline_model: baselineModel || undefined
      };
      const res = await getRecommendations(payload);
        setRecs(res.recommendations);
        setRecContext(res.context || null);
    } catch (err) {
      console.error(err);
      alert("Recommendation error: " + (err?.response?.data?.detail || err.message));
    }
  }

  // fetch models list when taskCategory changes
  React.useEffect(()=>{
    async function load() {
      if (!taskCategory) return setModelsForTask([]);
      try {
        const res = await getModelsForTask(taskCategory);
        setModelsForTask(res.models || []);
      } catch(e){
        console.error(e);
        setModelsForTask([]);
      }
    }
    load();
  }, [taskCategory]);

  return (
    <div className="app-root">
      <div className="app-shell">
        <header className="app-header">
          <h1 className="app-title">EcoAware Recommender</h1>
          <p className="app-subtitle">
            Visualize and choose AI models that balance accuracy, latency, and environmental impact.
          </p>
        </header>

        <div className="layout-grid">
          <TaskInput onTaskConfirmed={(cat) => setTaskCategory(cat)} />
          <ConstraintsPanel onChange={(c)=>{ setFilters(c); }} />
        </div>

        {taskCategory && (
          <div className="baseline-panel">
            <div style={{ marginBottom: 6, fontWeight: 500 }}>
              Optional baseline for <span style={{ fontStyle: "italic" }}>{taskCategory}</span>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8, alignItems: "center" }}>
              <select
                className="select-input"
                value={baselineModel}
                onChange={(e)=>setBaselineModel(e.target.value)}
              >
                <option value="">No baseline (compare models only)</option>
                {modelsForTask.map((m)=> (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
              <button
                className="secondary-button"
                onClick={async ()=>{
                  if (!baselineModel) return alert('Select a model or leave empty');
                  try {
                    await setBaseline(taskCategory, baselineModel);
                    alert('Baseline saved');
                  } catch(e){ console.error(e); alert('Could not save baseline') }
                }}
              >
                Save baseline
              </button>
            </div>
          </div>
        )}

        <div className="button-row" style={{ marginTop: 14 }}>
          <button className="primary-button" onClick={handleRecommend}>
            Get recommendations
          </button>
        </div>

        <ResultsTable recs={recs} context={recContext} />

        {recContext && (
          <div className="baseline-panel" style={{ marginTop: 12 }}>
            <div style={{ fontWeight: 600, marginBottom: 4 }}>Baseline diagnostics</div>
            <div><strong>Baseline input:</strong> {recContext.baseline_input ?? 'none'}</div>
            <div><strong>Baseline matched model:</strong> {recContext.baseline_matched_model ?? 'none'}</div>
            <div><strong>Baseline energy (Wh/1k):</strong> {recContext.baseline_energy_wh_per_1k ?? 'N/A'}</div>
            <div><strong>Baseline in task:</strong> {String(recContext.baseline_in_task)}</div>
            <div><strong>Baseline passed filters:</strong> {String(recContext.baseline_passed_filters)}</div>
            {recContext.baseline_note && (
              <div style={{ color: "#92400e", marginTop: 4 }}>
                <strong>Note:</strong> {recContext.baseline_note}
              </div>
            )}
          </div>
        )}

        <div className="charts-section">
          <TradeoffCharts recs={recs} />
        </div>
      </div>
    </div>
  );
}

export default App;

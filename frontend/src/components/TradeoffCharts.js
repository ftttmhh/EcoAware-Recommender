import React from "react";
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from "recharts";

/**
 * Trade-off visualizations for recommended models.
 * - Chart 1: Accuracy vs CO2 per 1k inferences
 * - Chart 2: Accuracy vs Energy (Wh per 1k inferences)
 *
 * Expects records shaped like the API response:
 * { model, accuracy, gpu_energy, co2_kg_per_1k, ... }
 */
export default function TradeoffCharts({ recs }) {
  if (!recs || recs.length === 0) return null;

  // Map recommendations into a chart-friendly array
  const points = recs.map((r) => ({
    name: r.model,
    accuracy: typeof r.accuracy === "number" ? r.accuracy : Number(r.accuracy) || 0,
    energy: typeof r.gpu_energy === "number" ? r.gpu_energy : Number(r.gpu_energy) || 0,
    co2: typeof r.co2_kg_per_1k === "number" ? r.co2_kg_per_1k : Number(r.co2_kg_per_1k) || 0
  }));

  return (
    <div style={{ marginTop: 24 }}>
      <h3>Trade-off visualizations</h3>

      <div style={{ height: 260, marginBottom: 24 }}>
        <h4 style={{ marginBottom: 8 }}>Accuracy vs CO₂ (kg per 1k inferences)</h4>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 0 }}>
            <CartesianGrid stroke="#e4d4c4" />
            <XAxis
              type="number"
              dataKey="accuracy"
              name="Accuracy"
              unit="%"
              tickFormatter={(v) => `${v}`}
            />
            <YAxis
              type="number"
              dataKey="co2"
              name="CO₂"
              unit=" kg/1k"
            />
            <Tooltip
              cursor={{ strokeDasharray: "3 3" }}
              formatter={(value, name) => {
                if (name === "accuracy") return [`${value}%`, "Accuracy"];
                if (name === "co2") return [`${value} kg`, "CO₂ per 1k"];
                return [value, name];
              }}
              labelFormatter={(_, payload) =>
                payload && payload[0] && payload[0].payload
                  ? payload[0].payload.name
                  : ""
              }
            />
            <Legend />
            <Scatter name="Models" data={points} fill="#865D36" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      <div style={{ height: 260 }}>
        <h4 style={{ marginBottom: 8 }}>Accuracy vs Energy (Wh per 1k inferences)</h4>
        <ResponsiveContainer width="100%" height="100%">
          <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 0 }}>
            <CartesianGrid stroke="#e4d4c4" />
            <XAxis
              type="number"
              dataKey="accuracy"
              name="Accuracy"
              unit="%"
              tickFormatter={(v) => `${v}`}
            />
            <YAxis
              type="number"
              dataKey="energy"
              name="Energy"
              unit=" Wh/1k"
            />
            <Tooltip
              cursor={{ strokeDasharray: "3 3" }}
              formatter={(value, name) => {
                if (name === "accuracy") return [`${value}%`, "Accuracy"];
                if (name === "energy") return [`${value} Wh`, "Energy per 1k"];
                return [value, name];
              }}
              labelFormatter={(_, payload) =>
                payload && payload[0] && payload[0].payload
                  ? payload[0].payload.name
                  : ""
              }
            />
            <Legend />
            <Scatter name="Models" data={points} fill="#AC8968" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}


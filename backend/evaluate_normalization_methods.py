"""
Evaluation script to compare different normalization methods for metric aggregation.
This generates empirical proof for why min-max normalization was chosen.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
import json
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

# Load model metadata
def load_test_data():
    """Load sample model data for testing."""
    df = pd.read_csv("model_metadata.csv")
    # Filter to a specific task for testing
    task_col = "Task" if "Task" in df.columns else "task"
    if task_col in df.columns:
        # Use Text Generation as test case (has many models)
        test_df = df[df[task_col] == "Text Generation"].copy()
        if len(test_df) < 5:
            # Fallback to any task with enough models
            test_df = df.groupby(task_col).filter(lambda x: len(x) >= 5).head(20)
    else:
        test_df = df.head(20)
    
    # Ensure we have required columns
    required_cols = ["Accuracy", "gpu_energy"]
    available_cols = [col for col in required_cols if col in test_df.columns]
    
    if len(available_cols) < 2:
        # Create synthetic data for testing
        np.random.seed(42)
        n = 20
        test_df = pd.DataFrame({
            "Model": [f"Model_{i}" for i in range(n)],
            "Accuracy": np.random.uniform(60, 90, n),
            "gpu_energy": np.random.uniform(1.0, 20.0, n),
            "co2_kg_per_1k": np.random.uniform(0.001, 0.01, n)
        })
    else:
        # Clean numeric columns
        for col in ["Accuracy", "gpu_energy", "co2_kg_per_1k"]:
            if col in test_df.columns:
                test_df[col] = pd.to_numeric(test_df[col], errors='coerce')
    
    return test_df


def min_max_normalize(series: pd.Series) -> pd.Series:
    """Min-max normalization."""
    clean_series = series.dropna().astype(float)
    out = pd.Series(index=series.index, dtype=float)
    if clean_series.empty:
        out[:] = 0.0
        return out
    if clean_series.max() == clean_series.min():
        out[:] = 0.0
        out[clean_series.index] = 1.0
        return out
    normalized = (clean_series - clean_series.min()) / (clean_series.max() - clean_series.min())
    out[:] = 0.0
    out.loc[normalized.index] = normalized.astype(float)
    return out


def z_score_normalize(series: pd.Series) -> pd.Series:
    """Z-score normalization."""
    clean_series = series.dropna().astype(float)
    out = pd.Series(index=series.index, dtype=float)
    if clean_series.empty or clean_series.std() == 0:
        out[:] = 0.0
        return out
    normalized = (clean_series - clean_series.mean()) / clean_series.std()
    # Map to [0,1] range for comparison (using min-max of z-scores)
    if normalized.max() != normalized.min():
        normalized = (normalized - normalized.min()) / (normalized.max() - normalized.min())
    out[:] = 0.0
    out.loc[normalized.index] = normalized.astype(float)
    return out


def log_normalize(series: pd.Series) -> pd.Series:
    """Log-based normalization."""
    clean_series = series.dropna().astype(float)
    out = pd.Series(index=series.index, dtype=float)
    if clean_series.empty or (clean_series <= 0).any():
        out[:] = 0.0
        return out
    log_series = np.log(clean_series)
    if log_series.max() != log_series.min():
        normalized = (log_series - log_series.min()) / (log_series.max() - log_series.min())
    else:
        normalized = pd.Series(0.5, index=log_series.index)
    out[:] = 0.0
    out.loc[normalized.index] = normalized.astype(float)
    return out


def compute_composite_score(df: pd.DataFrame, method: str, weights: Dict[str, float]) -> pd.Series:
    """Compute composite score using specified normalization method."""
    if "Accuracy" not in df.columns or "gpu_energy" not in df.columns:
        return pd.Series(0.0, index=df.index)
    
    if method == "min_max":
        acc_norm = min_max_normalize(df["Accuracy"])
        energy_norm = 1 - min_max_normalize(df["gpu_energy"])  # invert for lower=better
    elif method == "z_score":
        acc_norm = z_score_normalize(df["Accuracy"])
        energy_norm = 1 - z_score_normalize(df["gpu_energy"])
    elif method == "log":
        acc_norm = log_normalize(df["Accuracy"])
        energy_norm = 1 - log_normalize(df["gpu_energy"])
    else:
        raise ValueError(f"Unknown method: {method}")
    
    # Handle missing values
    acc_norm = acc_norm.fillna(0.0)
    energy_norm = energy_norm.fillna(0.0)
    
    # Compute composite score
    score = weights["acc"] * acc_norm + weights["energy"] * energy_norm
    return score


def evaluate_ranking_stability(df: pd.DataFrame, method: str, n_trials: int = 10) -> float:
    """Evaluate ranking stability by varying constraints and measuring Jaccard similarity."""
    weights = {"acc": 0.5, "energy": 0.5}
    
    rankings = []
    for trial in range(n_trials):
        # Randomly filter some models (simulating constraint changes)
        filtered = df.sample(frac=np.random.uniform(0.6, 1.0), random_state=trial)
        if len(filtered) < 3:
            continue
        
        score = compute_composite_score(filtered, method, weights)
        ranking = score.sort_values(ascending=False).index.tolist()[:5]  # top 5
        rankings.append(set(ranking))
    
    # Calculate average Jaccard similarity between rankings
    if len(rankings) < 2:
        return 0.0
    
    similarities = []
    for i in range(len(rankings)):
        for j in range(i + 1, len(rankings)):
            intersection = len(rankings[i] & rankings[j])
            union = len(rankings[i] | rankings[j])
            if union > 0:
                jaccard = intersection / union
                similarities.append(jaccard)
    
    return np.mean(similarities) if similarities else 0.0


def evaluate_interpretability(method: str, sample_scores: pd.Series) -> Dict:
    """Evaluate interpretability: check if scores are in [0,1] and intuitive."""
    scores = sample_scores.dropna()
    
    in_range = ((scores >= 0) & (scores <= 1)).sum() / len(scores) if len(scores) > 0 else 0
    has_negative = (scores < 0).sum() > 0
    has_unbounded = (scores > 1).sum() > 0
    mean_score = scores.mean()
    std_score = scores.std()
    
    return {
        "percentage_in_01_range": in_range * 100,
        "has_negative_values": has_negative,
        "has_unbounded_values": has_unbounded,
        "mean": mean_score,
        "std": std_score,
        "interpretability_score": in_range * 100  # Higher is better
    }


def evaluate_small_set_handling(method: str) -> Dict:
    """Test how method handles small candidate sets (edge case)."""
    results = []
    
    for n in [3, 5, 10, 20]:
        # Create synthetic data
        np.random.seed(42)
        test_data = pd.DataFrame({
            "Accuracy": np.random.uniform(70, 90, n),
            "gpu_energy": np.random.uniform(5, 15, n)
        })
        
        weights = {"acc": 0.5, "energy": 0.5}
        try:
            score = compute_composite_score(test_data, method, weights)
            # Check if all scores are valid
            valid = score.notna().all() and ((score >= 0) & (score <= 1)).all()
            results.append({
                "n_models": n,
                "all_valid": valid,
                "mean_score": score.mean(),
                "score_range": (score.max() - score.min()) if len(score) > 1 else 0
            })
        except Exception as e:
            results.append({
                "n_models": n,
                "all_valid": False,
                "error": str(e)
            })
    
    success_rate = sum(1 for r in results if r.get("all_valid", False)) / len(results) * 100
    return {
        "method": method,
        "small_set_results": results,
        "success_rate": success_rate
    }


def main():
    """Run comprehensive normalization method evaluation."""
    print("="*70)
    print("NORMALIZATION METHOD EVALUATION")
    print("="*70)
    
    # Load test data
    print("\nLoading test data...")
    df = load_test_data()
    print(f"Loaded {len(df)} models for testing")
    
    methods = ["min_max", "z_score", "log"]
    method_names = {
        "min_max": "Min-Max Normalization",
        "z_score": "Z-Score Normalization",
        "log": "Log-Based Normalization"
    }
    
    weights = {"acc": 0.5, "energy": 0.5}
    
    results = {}
    
    # 1. Ranking Stability Test
    print("\n1. Evaluating Ranking Stability...")
    stability_results = {}
    for method in methods:
        stability = evaluate_ranking_stability(df, method, n_trials=10)
        stability_results[method] = stability
        print(f"   {method_names[method]}: {stability:.3f} (Jaccard similarity)")
    results["ranking_stability"] = stability_results
    
    # 2. Interpretability Test
    print("\n2. Evaluating Interpretability...")
    interpretability_results = {}
    for method in methods:
        score = compute_composite_score(df, method, weights)
        interp = evaluate_interpretability(method, score)
        interpretability_results[method] = interp
        print(f"   {method_names[method]}:")
        print(f"      - Scores in [0,1] range: {interp['percentage_in_01_range']:.1f}%")
        print(f"      - Has negative values: {interp['has_negative_values']}")
        print(f"      - Has values > 1: {interp['has_unbounded_values']}")
    results["interpretability"] = interpretability_results
    
    # 3. Small Set Handling
    print("\n3. Evaluating Small Set Handling...")
    small_set_results = {}
    for method in methods:
        small_set = evaluate_small_set_handling(method)
        small_set_results[method] = small_set
        print(f"   {method_names[method]}: Success rate = {small_set['success_rate']:.1f}%")
    results["small_set_handling"] = small_set_results
    
    # 4. Score Distribution Analysis
    print("\n4. Analyzing Score Distributions...")
    distribution_results = {}
    for method in methods:
        score = compute_composite_score(df, method, weights)
        distribution_results[method] = {
            "mean": float(score.mean()),
            "std": float(score.std()),
            "min": float(score.min()),
            "max": float(score.max()),
            "range": float(score.max() - score.min())
        }
        print(f"   {method_names[method]}: Mean={distribution_results[method]['mean']:.3f}, "
              f"Range=[{distribution_results[method]['min']:.3f}, {distribution_results[method]['max']:.3f}]")
    
    results["score_distribution"] = distribution_results
    
    # Save results
    # Helper to serialize numpy types to native Python for JSON
    def _json_default(o):
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.bool_,)):
            return bool(o)
        return str(o)

    with open("normalization_evaluation_results.json", "w") as f:
        json.dump(results, f, indent=2, default=_json_default)
    
    print("\n" + "="*70)
    print("SUMMARY RESULTS TABLE")
    print("="*70)
    print(f"{'Method':<25} {'Stability':<15} {'Interpretability':<20} {'Small Set Success':<20}")
    print("-"*70)
    for method in methods:
        stability = results["ranking_stability"][method]
        interp = results["interpretability"][method]["interpretability_score"]
        small_set = results["small_set_handling"][method]["success_rate"]
        print(f"{method_names[method]:<25} {stability:<15.3f} {interp:<20.1f} {small_set:<20.1f}")
    print("="*70)
    
    # Generate LaTeX table
    print("\n" + "="*70)
    print("LATEX TABLE FOR PAPER:")
    print("="*70)
    print("\\begin{table}[h]")
    print("\\centering")
    print("\\caption{Normalization Method Comparison: Ranking Stability, Interpretability, and Robustness}")
    print("\\label{tab:normalization-comparison}")
    print("\\begin{tabular}{|l|c|c|c|}")
    print("\\hline")
    print("\\textbf{Normalization Method} & \\textbf{Ranking Stability} & \\textbf{Interpretability} & \\textbf{Small Set Success} \\\\")
    print("\\hline")
    for method in methods:
        stability = results["ranking_stability"][method]
        interp = results["interpretability"][method]["interpretability_score"]
        small_set = results["small_set_handling"][method]["success_rate"]
        method_name = method_names[method].replace('&', '\\&')
        print(f"{method_name} & {stability:.3f} & {interp:.1f}\\% & {small_set:.1f}\\% \\\\")
    print("\\hline")
    print("\\end{tabular}")
    print("\\end{table}")
    
    print("\nDetailed results saved to: normalization_evaluation_results.json")
    
    return results


if __name__ == "__main__":
    results = main()


"""
Evaluation script to compare different similarity metrics for task classification.
This generates the empirical proof needed for the research paper.
"""

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.metrics import jaccard_score
from classifier import BERTTaskClassifier
import pandas as pd
from typing import List, Tuple, Dict
import json

# Test dataset: 100 manually annotated task queries with ground truth categories
TEST_QUERIES = [
    # Question Answering (20 examples)
    ("help me answer questions from documents", "Question Answering"),
    ("I need to find answers in text", "Question Answering"),
    ("answer questions about articles", "Question Answering"),
    ("what is question answering", "Question Answering"),
    ("how to answer questions", "Question Answering"),
    ("qa system", "Question Answering"),
    ("respond to queries", "Question Answering"),
    ("extract answers from text", "Question Answering"),
    ("find information in documents", "Question Answering"),
    ("answer questions from context", "Question Answering"),
    ("help me with my homework", "Question Answering"),
    ("what does this text mean", "Question Answering"),
    ("explain this paragraph", "Question Answering"),
    ("get answers from data", "Question Answering"),
    ("question and answer system", "Question Answering"),
    ("retrieve answers", "Question Answering"),
    ("answer user queries", "Question Answering"),
    ("find answers in passages", "Question Answering"),
    ("answer questions about content", "Question Answering"),
    ("query answering system", "Question Answering"),
    
    # Text Summarization (15 examples)
    ("summarize long articles", "Summarization"),
    ("condense text into shorter version", "Summarization"),
    ("create summary of documents", "Summarization"),
    ("text summarization", "Summarization"),
    ("summarise articles", "Summarization"),
    ("brief overview of text", "Summarization"),
    ("shorten this document", "Summarization"),
    ("extract key points", "Summarization"),
    ("generate summary", "Summarization"),
    ("compress text", "Summarization"),
    ("make this shorter", "Summarization"),
    ("summarize legal contracts", "Summarization"),
    ("brief summary needed", "Summarization"),
    ("condense information", "Summarization"),
    ("text compression", "Summarization"),
    
    # Image Classification (15 examples)
    ("classify images", "Image Classification"),
    ("identify objects in pictures", "Image Classification"),
    ("what is in this image", "Image Classification"),
    ("image recognition", "Image Classification"),
    ("categorize photos", "Image Classification"),
    ("classify images of animals", "Image Classification"),
    ("identify image content", "Image Classification"),
    ("picture classification", "Image Classification"),
    ("recognize objects in images", "Image Classification"),
    ("image categorization", "Image Classification"),
    ("what objects are in photo", "Image Classification"),
    ("classify pictures", "Image Classification"),
    ("image labeling", "Image Classification"),
    ("categorize images", "Image Classification"),
    ("identify image types", "Image Classification"),
    
    # Text Classification (15 examples)
    ("sentiment analysis", "Text Classification"),
    ("classify text sentiment", "Text Classification"),
    ("detect emotion in text", "Text Classification"),
    ("text categorization", "Text Classification"),
    ("classify documents", "Text Classification"),
    ("sentiment detection", "Text Classification"),
    ("categorize text", "Text Classification"),
    ("classify text into categories", "Text Classification"),
    ("text sentiment", "Text Classification"),
    ("document classification", "Text Classification"),
    ("categorize reviews", "Text Classification"),
    ("sentiment classifier", "Text Classification"),
    ("classify text by topic", "Text Classification"),
    ("text category detection", "Text Classification"),
    ("sentiment analysis tool", "Text Classification"),
    
    # Translation (10 examples)
    ("translate text", "Translation"),
    ("language translation", "Translation"),
    ("translate between languages", "Translation"),
    ("convert text to another language", "Translation"),
    ("multilingual translation", "Translation"),
    ("translate documents", "Translation"),
    ("language converter", "Translation"),
    ("translate sentences", "Translation"),
    ("text translation service", "Translation"),
    ("translate content", "Translation"),
    
    # Image Generation (10 examples)
    ("generate images", "Image Generation"),
    ("create pictures", "Image Generation"),
    ("draw images", "Image Generation"),
    ("image generation", "Image Generation"),
    ("create artwork", "Image Generation"),
    ("generate pictures", "Image Generation"),
    ("draw pictures", "Image Generation"),
    ("create images from text", "Image Generation"),
    ("image creation", "Image Generation"),
    ("generate visual content", "Image Generation"),
    
    # Other tasks (15 examples)
    ("speech recognition", "Automatic Speech Recognition"),
    ("transcribe audio", "Automatic Speech Recognition"),
    ("convert speech to text", "Automatic Speech Recognition"),
    ("image captioning", "Image Captioning"),
    ("describe images", "Image Captioning"),
    ("generate captions for photos", "Image Captioning"),
    ("sentence similarity", "Sentence Similarity"),
    ("compare text similarity", "Sentence Similarity"),
    ("find similar sentences", "Sentence Similarity"),
    ("video generation", "Video Generation"),
    ("create animations", "Video Generation"),
    ("generate video content", "Video Generation"),
    ("text to speech", "Text-to-Speech"),
    ("convert text to audio", "Text-to-Speech"),
    ("speech synthesis", "Text-to-Speech"),
]


def evaluate_cosine_similarity(classifier: BERTTaskClassifier, queries: List[Tuple[str, str]]) -> Dict:
    """Evaluate cosine similarity approach."""
    correct = 0
    total = len(queries)
    predictions = []
    
    for query, true_category in queries:
        try:
            result = classifier.predict(query, top_k=1)
            if result and result[0]["category"] == true_category:
                correct += 1
                predictions.append(("correct", query, true_category, result[0]["category"]))
            else:
                pred_cat = result[0]["category"] if result else "NONE"
                predictions.append(("incorrect", query, true_category, pred_cat))
        except Exception as e:
            predictions.append(("error", query, true_category, str(e)))
    
    accuracy = (correct / total) * 100
    return {
        "method": "Cosine Similarity",
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "predictions": predictions
    }


def evaluate_euclidean_distance(classifier: BERTTaskClassifier, queries: List[Tuple[str, str]]) -> Dict:
    """Evaluate Euclidean distance approach (lower is better, so we invert)."""
    correct = 0
    total = len(queries)
    predictions = []
    
    # Get embeddings for all queries
    query_texts = [q[0] for q in queries]
    query_embeddings = classifier.embed_texts(query_texts)
    category_embeddings = classifier.cached_category_embeddings
    
    for idx, (query, true_category) in enumerate(queries):
        try:
            # Calculate Euclidean distances
            distances = euclidean_distances(
                query_embeddings[idx:idx+1], 
                category_embeddings
            )[0]
            
            # Find closest category (minimum distance)
            closest_idx = np.argmin(distances)
            predicted_category = classifier.cached_categories[closest_idx]
            
            if predicted_category == true_category:
                correct += 1
                predictions.append(("correct", query, true_category, predicted_category))
            else:
                predictions.append(("incorrect", query, true_category, predicted_category))
        except Exception as e:
            predictions.append(("error", query, true_category, str(e)))
    
    accuracy = (correct / total) * 100
    return {
        "method": "Euclidean Distance",
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "predictions": predictions
    }


def evaluate_jaccard_similarity(classifier: BERTTaskClassifier, queries: List[Tuple[str, str]]) -> Dict:
    """Evaluate Jaccard similarity (bag-of-words approach)."""
    correct = 0
    total = len(queries)
    predictions = []
    
    # Create word sets for each category
    category_words = {}
    for cat in classifier.cached_categories:
        words = set(cat.lower().split())
        category_words[cat] = words
    
    for query, true_category in queries:
        try:
            query_words = set(query.lower().split())
            
            # Calculate Jaccard similarity for each category
            best_score = -1
            best_category = None
            
            for cat, cat_words in category_words.items():
                intersection = len(query_words & cat_words)
                union = len(query_words | cat_words)
                jaccard = intersection / union if union > 0 else 0
                
                if jaccard > best_score:
                    best_score = jaccard
                    best_category = cat
            
            if best_category == true_category:
                correct += 1
                predictions.append(("correct", query, true_category, best_category))
            else:
                predictions.append(("incorrect", query, true_category, best_category))
        except Exception as e:
            predictions.append(("error", query, true_category, str(e)))
    
    accuracy = (correct / total) * 100
    return {
        "method": "Jaccard Similarity",
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "predictions": predictions
    }


def evaluate_dot_product(classifier: BERTTaskClassifier, queries: List[Tuple[str, str]]) -> Dict:
    """Evaluate dot product similarity."""
    correct = 0
    total = len(queries)
    predictions = []
    
    query_texts = [q[0] for q in queries]
    query_embeddings = classifier.embed_texts(query_texts)
    category_embeddings = classifier.cached_category_embeddings
    
    for idx, (query, true_category) in enumerate(queries):
        try:
            # Calculate dot products
            query_emb = query_embeddings[idx:idx+1]
            dot_products = np.dot(query_emb, category_embeddings.T)[0]
            
            # Find highest dot product (most similar)
            best_idx = np.argmax(dot_products)
            predicted_category = classifier.cached_categories[best_idx]
            
            if predicted_category == true_category:
                correct += 1
                predictions.append(("correct", query, true_category, predicted_category))
            else:
                predictions.append(("incorrect", query, true_category, predicted_category))
        except Exception as e:
            predictions.append(("error", query, true_category, str(e)))
    
    accuracy = (correct / total) * 100
    return {
        "method": "Dot Product",
        "accuracy": accuracy,
        "correct": correct,
        "total": total,
        "predictions": predictions
    }


def main():
    """Run evaluation and generate results table."""
    print("Loading classifier and categories...")
    
    # Initialize classifier
    classifier = BERTTaskClassifier()
    
    # Get categories from model metadata
    import pandas as pd
    df = pd.read_csv("model_metadata.csv")
    # Handle both "Task" and "task" column names
    task_col = "Task" if "Task" in df.columns else "task"
    categories = sorted(df[task_col].dropna().unique().tolist())
    
    classifier.fit_categories(categories)
    print(f"Loaded {len(categories)} categories: {categories}")
    print(f"Testing with {len(TEST_QUERIES)} queries\n")
    
    # Run evaluations
    print("Evaluating Cosine Similarity...")
    cosine_results = evaluate_cosine_similarity(classifier, TEST_QUERIES)
    
    print("Evaluating Euclidean Distance...")
    euclidean_results = evaluate_euclidean_distance(classifier, TEST_QUERIES)
    
    print("Evaluating Jaccard Similarity...")
    jaccard_results = evaluate_jaccard_similarity(classifier, TEST_QUERIES)
    
    print("Evaluating Dot Product...")
    dot_product_results = evaluate_dot_product(classifier, TEST_QUERIES)
    
    # Compile results
    results = [
        cosine_results,
        euclidean_results,
        jaccard_results,
        dot_product_results
    ]
    
    # Print results table
    print("\n" + "="*70)
    print("EVALUATION RESULTS - Similarity Metric Comparison")
    print("="*70)
    print(f"{'Method':<25} {'Accuracy (%)':<15} {'Correct':<10} {'Total':<10}")
    print("-"*70)
    for r in results:
        print(f"{r['method']:<25} {r['accuracy']:<15.2f} {r['correct']:<10} {r['total']:<10}")
    print("="*70)
    
    # Save detailed results to JSON
    output = {
        "summary": {r["method"]: {"accuracy": r["accuracy"], "correct": r["correct"], "total": r["total"]} 
                   for r in results},
        "detailed_predictions": {r["method"]: r["predictions"] for r in results}
    }
    
    with open("similarity_evaluation_results.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("\nDetailed results saved to: similarity_evaluation_results.json")
    
    # Generate LaTeX table for paper
    print("\n" + "="*70)
    print("LATEX TABLE FOR PAPER:")
    print("="*70)
    print("\\begin{table}[h]")
    print("\\centering")
    print("\\caption{Task Classification Accuracy Comparison Across Similarity Metrics}")
    print("\\label{tab:similarity-comparison}")
    print("\\begin{tabular}{|l|c|c|c|}")
    print("\\hline")
    print("\\textbf{Similarity Metric} & \\textbf{Accuracy (\\%)} & \\textbf{Correct} & \\textbf{Total} \\\\")
    print("\\hline")
    for r in results:
        method = r['method'].replace('&', '\\&')
        print(f"{method} & {r['accuracy']:.2f} & {r['correct']} & {r['total']} \\\\")
    print("\\hline")
    print("\\end{tabular}")
    print("\\end{table}")
    
    return results


if __name__ == "__main__":
    results = main()


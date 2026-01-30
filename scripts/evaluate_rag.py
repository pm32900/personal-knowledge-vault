#!/usr/bin/env python3
"""
RAG System Evaluation Script

Evaluates retrieval quality and answer generation performance using:
- Precision@K and Recall@K for retrieval accuracy
- Mean Reciprocal Rank (MRR) for ranking quality
- Latency measurements for performance monitoring

Usage:
    python scripts/evaluate_rag.py --dataset data/eval_queries.json --k 5
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import List, Dict, Set, Any
import requests

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.evaluation.metrics import evaluate_retrieval, EvaluationResult


def load_evaluation_dataset(filepath: str) -> List[Dict[str, Any]]:
    """Load evaluation queries with ground truth from JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def run_search_query(query: str, token: str, k: int = 5, base_url: str = "http://localhost:8001") -> tuple:
    """
    Execute semantic search query and measure latency.
    
    Returns:
        Tuple of (retrieved_note_ids, latency_ms)
    """
    start_time = time.perf_counter()
    
    response = requests.get(
        f"{base_url}/api/v1/search/",
        params={"query": query, "top_k": k},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    end_time = time.perf_counter()
    latency_ms = (end_time - start_time) * 1000
    
    if response.status_code != 200:
        print(f"Error searching for '{query}': {response.status_code}")
        return [], latency_ms
    
    results = response.json()
    note_ids = [result["note_id"] for result in results]
    
    return note_ids, latency_ms


def authenticate(email: str, password: str, base_url: str = "http://localhost:8001") -> str:
    """Authenticate and return JWT token."""
    response = requests.post(
        f"{base_url}/api/v1/auth/login",
        json={"email": email, "password": password}
    )
    
    if response.status_code != 200:
        raise Exception(f"Authentication failed: {response.json()}")
    
    return response.json()["access_token"]


def run_evaluation(
    dataset_path: str,
    k: int = 5,
    email: str = "test@example.com",
    password: str = "testpass123",
    base_url: str = "http://localhost:8001"
) -> EvaluationResult:
    """
    Run complete evaluation on the dataset.
    
    Args:
        dataset_path: Path to evaluation dataset JSON
        k: Number of top results to evaluate
        email: User email for authentication
        password: User password
        base_url: API base URL
        
    Returns:
        EvaluationResult with all metrics
    """
    # Load dataset
    print(f"Loading evaluation dataset from {dataset_path}...")
    dataset = load_evaluation_dataset(dataset_path)
    print(f"Loaded {len(dataset)} evaluation queries\n")
    
    # Authenticate
    print("Authenticating...")
    token = authenticate(email, password, base_url)
    print("✓ Authenticated\n")
    
    # Run queries
    queries = []
    retrieved_results = []
    ground_truth = []
    latencies = []
    
    print(f"Running evaluation (k={k})...")
    for i, item in enumerate(dataset, 1):
        query = item["query"]
        relevant_ids = set(item["relevant_note_ids"])
        
        queries.append(query)
        ground_truth.append(relevant_ids)
        
        # Execute search
        retrieved_ids, latency = run_search_query(query, token, k, base_url)
        retrieved_results.append(retrieved_ids)
        latencies.append(latency)
        
        print(f"  [{i}/{len(dataset)}] Query: '{query[:50]}...' | Latency: {latency:.2f}ms")
    
    # Calculate metrics
    print("\nCalculating metrics...")
    result = evaluate_retrieval(
        queries=queries,
        retrieved_results=retrieved_results,
        ground_truth=ground_truth,
        k=k,
        latencies=latencies
    )
    
    return result


def print_results(result: EvaluationResult):
    """Pretty print evaluation results."""
    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    print(f"Total Queries:     {result.total_queries}")
    print(f"K:                 {result.k}")
    print(f"\nRetrieval Metrics:")
    print(f"  Precision@{result.k}:    {result.precision_at_k:.4f}")
    print(f"  Recall@{result.k}:       {result.recall_at_k:.4f}")
    print(f"  MRR:             {result.mrr:.4f}")
    print(f"\nPerformance:")
    print(f"  Avg Latency:     {result.latency_ms:.2f} ms")
    print(f"\nTimestamp:         {result.timestamp}")
    print("="*60 + "\n")


def save_results(result: EvaluationResult, output_path: str):
    """Save evaluation results to JSON file."""
    with open(output_path, 'w') as f:
        json.dump(result.to_dict(), f, indent=2)
    print(f"✓ Results saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Evaluate RAG system performance")
    parser.add_argument(
        "--dataset",
        type=str,
        default="data/eval_queries.json",
        help="Path to evaluation dataset JSON file"
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of top results to evaluate (default: 5)"
    )
    parser.add_argument(
        "--email",
        type=str,
        default="test@example.com",
        help="User email for authentication"
    )
    parser.add_argument(
        "--password",
        type=str,
        default="testpass123",
        help="User password"
    )
    parser.add_argument(
        "--base-url",
        type=str,
        default="http://localhost:8001",
        help="API base URL"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="evaluation_results.json",
        help="Output file for results"
    )
    
    args = parser.parse_args()
    
    try:
        # Run evaluation
        result = run_evaluation(
            dataset_path=args.dataset,
            k=args.k,
            email=args.email,
            password=args.password,
            base_url=args.base_url
        )
        
        # Print and save results
        print_results(result)
        save_results(result, args.output)
        
    except FileNotFoundError:
        print(f"Error: Dataset file '{args.dataset}' not found")
        print("Create an evaluation dataset first. See data/eval_queries.json.example")
        sys.exit(1)
    except Exception as e:
        print(f"Error during evaluation: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

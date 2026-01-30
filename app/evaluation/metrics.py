"""
Evaluation metrics for RAG system performance.

Includes:
- Precision@K and Recall@K for retrieval quality
- Mean Reciprocal Rank (MRR) for ranking quality
- Latency measurement for performance monitoring
"""

from typing import List, Set, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import time
from functools import wraps


@dataclass
class EvaluationResult:
    """Container for evaluation metrics."""
    precision_at_k: float
    recall_at_k: float
    mrr: float
    latency_ms: float
    k: int
    total_queries: int
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "precision_at_k": round(self.precision_at_k, 4),
            "recall_at_k": round(self.recall_at_k, 4),
            "mrr": round(self.mrr, 4),
            "latency_ms": round(self.latency_ms, 2),
            "k": self.k,
            "total_queries": self.total_queries,
            "timestamp": self.timestamp
        }


def calculate_precision_at_k(
    retrieved: List[int],
    relevant: Set[int],
    k: int
) -> float:
    """
    Calculate Precision@K.
    
    Precision@K = (# of relevant items in top-K) / K
    
    Args:
        retrieved: List of retrieved note IDs in ranked order
        relevant: Set of ground-truth relevant note IDs
        k: Number of top results to consider
        
    Returns:
        Precision@K score (0.0 to 1.0)
    """
    if k <= 0 or not retrieved:
        return 0.0
    
    top_k = retrieved[:k]
    relevant_in_top_k = sum(1 for note_id in top_k if note_id in relevant)
    
    return relevant_in_top_k / k


def calculate_recall_at_k(
    retrieved: List[int],
    relevant: Set[int],
    k: int
) -> float:
    """
    Calculate Recall@K.
    
    Recall@K = (# of relevant items in top-K) / (total # of relevant items)
    
    Args:
        retrieved: List of retrieved note IDs in ranked order
        relevant: Set of ground-truth relevant note IDs
        k: Number of top results to consider
        
    Returns:
        Recall@K score (0.0 to 1.0)
    """
    if not relevant or k <= 0:
        return 0.0
    
    top_k = retrieved[:k]
    relevant_in_top_k = sum(1 for note_id in top_k if note_id in relevant)
    
    return relevant_in_top_k / len(relevant)


def calculate_mrr(
    retrieved_lists: List[List[int]],
    relevant_sets: List[Set[int]]
) -> float:
    """
    Calculate Mean Reciprocal Rank (MRR) across multiple queries.
    
    MRR = average of (1 / rank of first relevant item) for each query
    
    Args:
        retrieved_lists: List of retrieved note ID lists (one per query)
        relevant_sets: List of relevant note ID sets (one per query)
        
    Returns:
        MRR score (0.0 to 1.0)
    """
    if not retrieved_lists or len(retrieved_lists) != len(relevant_sets):
        return 0.0
    
    reciprocal_ranks = []
    
    for retrieved, relevant in zip(retrieved_lists, relevant_sets):
        rank = None
        for i, note_id in enumerate(retrieved, start=1):
            if note_id in relevant:
                rank = i
                break
        
        if rank is not None:
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)
    
    return sum(reciprocal_ranks) / len(reciprocal_ranks) if reciprocal_ranks else 0.0


def measure_latency(func):
    """
    Decorator to measure function execution time in milliseconds.
    
    Usage:
        @measure_latency
        def my_function():
            ...
    
    Returns:
        Tuple of (result, latency_ms)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        return result, latency_ms
    return wrapper


def evaluate_retrieval(
    queries: List[str],
    retrieved_results: List[List[int]],
    ground_truth: List[Set[int]],
    k: int = 5,
    latencies: List[float] = None
) -> EvaluationResult:
    """
    Comprehensive evaluation of retrieval performance.
    
    Args:
        queries: List of query strings
        retrieved_results: List of retrieved note ID lists (one per query)
        ground_truth: List of relevant note ID sets (one per query)
        k: Number of top results to consider for P@K and R@K
        latencies: Optional list of latency measurements in ms
        
    Returns:
        EvaluationResult with all metrics
    """
    if not queries or len(queries) != len(retrieved_results) != len(ground_truth):
        raise ValueError("Queries, results, and ground truth must have same length")
    
    # Calculate average Precision@K
    precisions = [
        calculate_precision_at_k(retrieved, relevant, k)
        for retrieved, relevant in zip(retrieved_results, ground_truth)
    ]
    avg_precision = sum(precisions) / len(precisions)
    
    # Calculate average Recall@K
    recalls = [
        calculate_recall_at_k(retrieved, relevant, k)
        for retrieved, relevant in zip(retrieved_results, ground_truth)
    ]
    avg_recall = sum(recalls) / len(recalls)
    
    # Calculate MRR
    mrr = calculate_mrr(retrieved_results, ground_truth)
    
    # Calculate average latency
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    
    return EvaluationResult(
        precision_at_k=avg_precision,
        recall_at_k=avg_recall,
        mrr=mrr,
        latency_ms=avg_latency,
        k=k,
        total_queries=len(queries)
    )

# Evaluation Data

This directory contains datasets for evaluating RAG system performance.

## Files

- `eval_queries.json` - Sample evaluation queries with ground truth relevance judgments

## Dataset Format

Each evaluation query should have:

```json
{
  "query": "Your search query",
  "relevant_note_ids": [1, 2, 3],
  "description": "Optional description of what this tests"
}
```

## Creating Your Own Dataset

1. Create notes in your knowledge vault
2. Record the note IDs
3. Create queries that should retrieve those notes
4. Add to `eval_queries.json` with the relevant note IDs

## Running Evaluation

```bash
python scripts/evaluate_rag.py --dataset data/eval_queries.json --k 5
```

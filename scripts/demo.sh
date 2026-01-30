#!/bin/bash
# Demo script for recording Personal Knowledge Vault functionality
# This script demonstrates the complete RAG workflow

set -e

BASE_URL="http://localhost:8001"
EMAIL="demo@example.com"
PASSWORD="demopass123"

echo "=================================================="
echo "Personal Knowledge Vault - Demo Script"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Register User
echo -e "${BLUE}Step 1: Registering user...${NC}"
REGISTER_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")
echo -e "${GREEN}✓ User registered${NC}"
echo "$REGISTER_RESPONSE" | jq '.'
echo ""

# Step 2: Login
echo -e "${BLUE}Step 2: Logging in...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
echo -e "${GREEN}✓ Logged in successfully${NC}"
echo "Token: ${TOKEN:0:50}..."
echo ""

# Step 3: Create Notes
echo -e "${BLUE}Step 3: Creating notes about machine learning...${NC}"

NOTE1=$(curl -s -X POST "$BASE_URL/api/v1/notes/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Neural Networks Basics",
    "content": "Neural networks are computing systems inspired by biological neural networks. They consist of layers of interconnected nodes (neurons) that process information. Each connection has a weight that adjusts during training through backpropagation.",
    "tags": ["ml", "neural-networks", "deep-learning"]
  }')
echo -e "${GREEN}✓ Created note 1: Neural Networks Basics${NC}"

NOTE2=$(curl -s -X POST "$BASE_URL/api/v1/notes/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Gradient Descent Optimization",
    "content": "Gradient descent is an optimization algorithm used to minimize the loss function in machine learning models. It iteratively adjusts parameters in the direction of steepest descent of the loss function. Learning rate controls step size.",
    "tags": ["ml", "optimization", "algorithms"]
  }')
echo -e "${GREEN}✓ Created note 2: Gradient Descent Optimization${NC}"

NOTE3=$(curl -s -X POST "$BASE_URL/api/v1/notes/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Convolutional Neural Networks",
    "content": "CNNs are specialized neural networks for processing grid-like data such as images. They use convolutional layers that apply filters to detect features like edges, textures, and patterns. Commonly used in computer vision tasks.",
    "tags": ["ml", "cnn", "computer-vision"]
  }')
echo -e "${GREEN}✓ Created note 3: Convolutional Neural Networks${NC}"
echo ""

# Step 4: List All Notes
echo -e "${BLUE}Step 4: Listing all notes...${NC}"
NOTES=$(curl -s -X GET "$BASE_URL/api/v1/notes/" \
  -H "Authorization: Bearer $TOKEN")
echo "$NOTES" | jq '.[] | {id, title, tags}'
echo ""

# Step 5: Semantic Search
echo -e "${BLUE}Step 5: Performing semantic search...${NC}"
echo -e "${YELLOW}Query: 'How do neural networks learn?'${NC}"
SEARCH_RESULTS=$(curl -s -X GET "$BASE_URL/api/v1/search/?query=How%20do%20neural%20networks%20learn&top_k=3" \
  -H "Authorization: Bearer $TOKEN")
echo "$SEARCH_RESULTS" | jq '.[] | {note_id, title, similarity, excerpt}'
echo ""

# Step 6: RAG Question Answering
echo -e "${BLUE}Step 6: Asking question with RAG...${NC}"
echo -e "${YELLOW}Question: 'What optimization algorithm is used to train neural networks?'${NC}"
RAG_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/rag/ask?query=What%20optimization%20algorithm%20is%20used%20to%20train%20neural%20networks" \
  -H "Authorization: Bearer $TOKEN")
echo -e "${GREEN}Answer:${NC}"
echo "$RAG_RESPONSE" | jq -r '.answer'
echo ""
echo -e "${GREEN}Citations:${NC}"
echo "$RAG_RESPONSE" | jq '.citations[] | {note_id, title, similarity}'
echo ""

# Step 7: Update a Note
echo -e "${BLUE}Step 7: Updating a note...${NC}"
NOTE1_ID=$(echo "$NOTE1" | jq -r '.id')
UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/api/v1/notes/$NOTE1_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Neural Networks Basics - Updated",
    "content": "Neural networks are computing systems inspired by biological neural networks. They consist of layers of interconnected nodes (neurons) that process information. Each connection has a weight that adjusts during training through backpropagation. Modern deep learning uses multiple hidden layers for complex pattern recognition."
  }')
echo -e "${GREEN}✓ Note updated${NC}"
echo "$UPDATE_RESPONSE" | jq '{id, title, updated_at}'
echo ""

# Step 8: Delete a Note
echo -e "${BLUE}Step 8: Deleting a note...${NC}"
NOTE3_ID=$(echo "$NOTE3" | jq -r '.id')
curl -s -X DELETE "$BASE_URL/api/v1/notes/$NOTE3_ID" \
  -H "Authorization: Bearer $TOKEN"
echo -e "${GREEN}✓ Note deleted (ID: $NOTE3_ID)${NC}"
echo ""

# Final Summary
echo "=================================================="
echo -e "${GREEN}Demo completed successfully!${NC}"
echo "=================================================="
echo ""
echo "Demonstrated features:"
echo "  ✓ User registration and authentication"
echo "  ✓ CRUD operations on notes"
echo "  ✓ Semantic search with similarity scores"
echo "  ✓ RAG-based question answering with citations"
echo ""
echo "To record this demo as a GIF, use:"
echo "  asciinema rec demo.cast"
echo "  ./scripts/demo.sh"
echo "  exit"
echo "  agg demo.cast demo.gif"

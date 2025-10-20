import numpy as np
from typing import List, Tuple

def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    if not a or not b or len(a) != len(b):
        return 0.0
    
    # Convert to numpy arrays
    vec_a = np.array(a)
    vec_b = np.array(b)
    
    # Calculate cosine similarity
    dot_product = np.dot(vec_a, vec_b)
    norm_a = np.linalg.norm(vec_a)
    norm_b = np.linalg.norm(vec_b)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    return dot_product / (norm_a * norm_b)

def find_top_similar_episodes(
    query_embedding: List[float], 
    episodes: List[dict], 
    top_k: int = 5
) -> List[dict]:
    """Find top-k most similar episodes to query embedding"""
    if not query_embedding or not episodes:
        return []
    
    # Calculate similarities
    similarities = []
    for episode in episodes:
        if 'embedding' in episode and episode['embedding']:
            similarity = cosine_similarity(query_embedding, episode['embedding'])
            similarities.append((episode, similarity))
    
    # Sort by similarity (descending) and return top-k
    similarities.sort(key=lambda x: x[1], reverse=True)
    return [episode for episode, _ in similarities[:top_k]]

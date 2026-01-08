# Vector Database Benchmark Report
**Dataset:** 500K Vectors | **Dimensions:** 1536 | **Metric:** Cosine Similarity

## 1. Executive Summary
This benchmark evaluates the performance of **VectorChord**, **PgVector**, **Weaviate**, and **MariaDB**. We analyze the fundamental tradeoff between **Search Throughput (QPS)** and **Search Quality (Recall)**. VectorChord currently defines the "speed" frontier, while Weaviate and PgVector offer balanced "reliability" profiles for different connectivity needs.

## 2. Comparative Performance Table

| Database        | Index Type          | Config (m/efc)   | Max QPS     | Recall     | P99 Latency | Tradeoff Profile |
|:----------------|:--------------------|:-----------------|:------------|:-----------|:------------|:-----------------|
| **VectorChord** | **Graph (`vchordg`)** | **m: 24, efc: 128**| **1061.06** | 0.8736     | **0.025s**  | **Ultra-Fast / High Accuracy** |
| **VectorChord** | Graph (`vchordg`)   | m: 16, efc: 128  | 947.01      | 0.8625     | 0.029s      | High-Speed / High Accuracy |
| **PgVector**    | HNSW                | m: 8, efc: 64    | 187.31      | **0.8829** | 0.119s      | Moderate Speed / **Peak Accuracy** |
| **Weaviate**    | HNSW                | m: 24, efc: 128  | 28.14       | 0.8541     | 0.312s      | Balanced / High Recall |
| **Weaviate**    | HNSW                | m: 16, efc: 128  | 33.82       | 0.8329     | 0.298s      | Balanced / Mid-High Recall |
| **Weaviate**    | HNSW                | m: 8, efc: 64    | 39.55       | 0.8172     | 0.285s      | Balanced / Mid Recall |
| **VectorChord** | RQ (`vchordrq`)     | Lists: 1024      | 699.49      | 0.7586     | 0.042s      | Fast / Mid Accuracy |
| **MariaDB**     | HNSW                | m: 16, efc: 128  | 44.27       | 0.6475     | 0.143s      | Relational / Low Recall |

---

## 3. The QPS-Recall Frontier

The data reveals a clear inverse correlation: as you aim for higher accuracy (Recall), you must sacrifice throughput (QPS).

### ⚖️ The Tradeoff Breakdown:
*   **VectorChord (The Speed Leader):** Demonstrates that modern graph implementations can achieve near-peak accuracy while staying above 1000 QPS. Its `m: 24` configuration is currently the "Gold Standard" for this benchmark.
*   **Weaviate (The Stability Pillar):** Showcases a very linear tradeoff. Increasing `m` from 8 to 24 improved recall by **~3.7%**, but resulted in a **28% decrease in QPS**. This is a classic HNSW behavior where more connections lead to more thorough (but slower) graph traversals.
*   **PgVector (The Precision Specialist):** Even with a lower `m: 8`, it maintains the highest raw recall (**0.88+**). It prioritizes the quality of the neighbor graph over the speed of traversal.

## 4. Technical Conclusion
For production environments:
1.  **Use VectorChord (`vchordg`, m: 24)** if you need the absolute highest throughput without sacrificing significant accuracy.
2.  **Use PgVector** if your application is highly sensitive to missing results (Recall > 0.88) and can tolerate 100ms+ latencies.
3.  **Use Weaviate** for cloud-native workflows that require predictable, steady scaling as you tune for higher accuracy.
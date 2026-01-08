import os
import json
import matplotlib.pyplot as plt
from collections import defaultdict

def extract_data(results_dir):
    data = defaultdict(list)
    for root, dirs, files in os.walk(results_dir):
        for file in files:
            if file.endswith(".json") and file.startswith("result_"):
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        content = json.load(f)
                        if "results" in content:
                            for res in content["results"]:
                                metrics = res.get("metrics", {})
                                task_config = res.get("task_config", {})
                                db_name = task_config.get("db", "Unknown")
                                if db_name == "VectorChord":
                                    db_case_config = task_config.get("db_case_config", {})
                                    index_method = db_case_config.get("index_method")
                                    if index_method in ["vchordrq", "vchordg"]:
                                        db_name = index_method
                                qps = metrics.get("qps")
                                recall = metrics.get("recall")
                                if qps is not None and recall is not None:
                                    data[db_name].append({"qps": qps, "recall": recall})
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
    return data

def generate_chart(data, output_file):
    plt.figure(figsize=(10, 6))
    for db_name, points in data.items():
        # Sort points by recall for better line plotting
        points.sort(key=lambda x: x["recall"])
        recalls = [p["recall"] for p in points]
        qps_values = [p["qps"] for p in points]
        
        plt.plot(recalls, qps_values, marker='o', label=db_name)
        for i, (r, q) in enumerate(zip(recalls, qps_values)):
            plt.annotate(f"{q:.1f}", (r, q), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8)

    plt.xlabel('Recall')
    plt.ylabel('QPS')
    plt.title('Vector Database Benchmark: QPS vs Recall')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Chart saved to {output_file}")

if __name__ == "__main__":
    results_path = os.path.join("vectordb_bench", "results")
    extracted_data = extract_data(results_path)
    if not extracted_data:
        print("No data found to plot.")
    else:
        generate_chart(extracted_data, "qps_vs_recall.png")

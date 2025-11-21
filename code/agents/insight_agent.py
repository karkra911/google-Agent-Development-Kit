from shared.dataset import Dataset

class InsightAgent:
    def __init__(self):
        pass

    def analyze(self, dataset):
        insights = []
        
        if not dataset:
            return ["No dataset to analyze."]

        row_count = dataset.get_total_rows()
        insights.append(f"Total rows in dataset: {row_count}")

        sum_val = 0
        count = 0
        
        for row in dataset.get_rows():
            if len(row) > 1:
                val = row[1]
                if isinstance(val, (int, float)):
                    sum_val += val
                    count += 1
                elif isinstance(val, str) and val.replace('.', '', 1).isdigit():
                     sum_val += float(val)
                     count += 1

        if count > 0:
            avg = sum_val / count
            insights.append(f"Average value of second column: {avg}")
        else:
            insights.append("No numeric data found in second column for analysis.")

        return insights

if __name__ == "__main__":
    print("InsightAgent: Please use this agent with a Dataset from QueryAgent.")

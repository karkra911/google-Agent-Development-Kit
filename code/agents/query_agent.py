import csv
from shared.agent_config import AgentConfig
from shared.dataset import Dataset

class QueryAgent:
    def __init__(self, config):
        self.config = config

    def run_query(self):
        print("QueryAgent: Reading data from local source...")
        source_file = self.config.get_query_source_file()
        
        headers = []
        rows = []
        
        try:
            # In a real scenario, we would read the CSV file at sourceFile
            # For now, we mock it as per the Java version, or try to read if exists
            if source_file and False: # Disable real read for now to match mock behavior
                 with open(source_file, 'r') as f:
                    reader = csv.reader(f)
                    headers = next(reader)
                    for row in reader:
                        rows.append(row)
            else:
                # Mock data
                headers = ["id", "value"]
                rows = [
                    ["1", 100],
                    ["2", 200]
                ]

            dataset = Dataset(headers, rows)
            print("QueryAgent: Data retrieved successfully.")
            return dataset
        except Exception as e:
            print(f"QueryAgent: Failed to query data - {e}")
            return None

if __name__ == "__main__":
    config = AgentConfig("../config/config.json")
    agent = QueryAgent(config)
    agent.run_query()

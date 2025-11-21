import time
import threading
import requests
from shared.agent_config import AgentConfig
from shared.storage_helper import StorageHelper

class IngestionAgent:
    def __init__(self, config):
        self.config = config
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._run_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _run_loop(self):
        while self.running:
            self._ingest_task()
            time.sleep(self.config.get_ingestion_interval_ms() / 1000)

    def _ingest_task(self):
        try:
            print("IngestionAgent: Fetching data from source...")
            url = self.config.get_source_url()
            response = requests.get(url)
            response.raise_for_status()
            
            raw_data = response.text
            StorageHelper.save_to_file(raw_data, self.config.get_storage_output_path())
            print("IngestionAgent: Data ingested and saved.")
        except Exception as e:
            print(f"IngestionAgent: Failed to ingest data: {e}")

if __name__ == "__main__":
    config = AgentConfig("../config/config.json")
    agent = IngestionAgent(config)
    agent.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        agent.stop()

import json
import os

class AgentConfig:
    def __init__(self, config_file_path):
        self.source_url = None
        self.storage_input_path = None
        self.storage_output_path = None
        self.query_source_file = None
        self.ingestion_interval_ms = 0
        self.load_config(config_file_path)

    def load_config(self, path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                
                agents = data.get("agents", {})
                ingestion = agents.get("ingestion", {})
                
                self.source_url = ingestion.get("source_url")
                interval_minutes = ingestion.get("fetch_interval_minutes", 30)
                self.ingestion_interval_ms = interval_minutes * 60 * 1000
                
                if "query" in agents:
                    query = agents.get("query", {})
                    self.query_source_file = query.get("source_file")
                
                storage = data.get("local_storage", {})
                self.storage_input_path = storage.get("input_path")
                self.storage_output_path = storage.get("output_path")
                
        except Exception as e:
            print(f"AgentConfig: Failed to load config - {e}")

    def get_source_url(self):
        return self.source_url

    def get_storage_input_path(self):
        return self.storage_input_path

    def get_storage_output_path(self):
        return self.storage_output_path
    
    def get_query_source_file(self):
        return self.query_source_file

    def get_ingestion_interval_ms(self):
        return self.ingestion_interval_ms

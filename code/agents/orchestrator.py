import time
import sys
import os

# Add code directory to sys.path to allow imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.agent_config import AgentConfig
from agents.ingestion_agent import IngestionAgent
from agents.query_agent import QueryAgent
from agents.insight_agent import InsightAgent
from agents.presentation_agent import PresentationAgent

class Orchestrator:
    def run(self):
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.json')
        config = AgentConfig(config_path)

        # Step 1: Ingest data
        ingestion_agent = IngestionAgent(config)
        ingestion_agent.start()
        
        # Wait for ingestion to complete (simulate for demo)
        time.sleep(5)
        ingestion_agent.stop()

        # Step 2: Query data
        query_agent = QueryAgent(config)
        query_result = query_agent.run_query()

        # Step 3: Analyze data
        insight_agent = InsightAgent()
        insights = insight_agent.analyze(query_result)

        # Step 4: Present insights
        presentation_agent = PresentationAgent()
        presentation_agent.present(insights)

if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.run()

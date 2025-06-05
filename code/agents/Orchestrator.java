package agents;

import shared.AgentConfig;
import com.google.cloud.bigquery.TableResult;
import java.util.List;

public class Orchestrator {
    public static void main(String[] args) {
        // Load configuration
        AgentConfig config = new AgentConfig("config/config.json");

        // Step 1: Ingest data
        IngestionAgent ingestionAgent = new IngestionAgent(config);
        ingestionAgent.start();
        // Wait for ingestion to complete (simulate for demo)
        try { Thread.sleep(5000); } catch (InterruptedException e) {}

        // Step 2: Query data
        QueryAgent queryAgent = new QueryAgent(config);
        TableResult queryResult = null;
        try {
            queryResult = queryAgent.runQuery();
        } catch (Exception e) {
            System.err.println("Orchestrator: Query failed - " + e.getMessage());
            return;
        }

        // Step 3: Analyze data
        InsightAgent insightAgent = new InsightAgent();
        List<String> insights = insightAgent.analyze(queryResult);

        // Step 4: Present insights
        PresentationAgent presentationAgent = new PresentationAgent();
        presentationAgent.present(insights);
    }
}

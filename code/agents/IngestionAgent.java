package agents;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.URL;
import java.util.Timer;
import java.util.TimerTask;

import shared.AgentConfig;
import shared.StorageHelper;

/**
 * IngestionAgent autonomously collects data from a configured source URL and saves it to storage.
 * Usage: Instantiate with AgentConfig and call start().
 */
public class IngestionAgent {

    private final AgentConfig config;

    public IngestionAgent(AgentConfig config) {
        this.config = config;
    }

    public void start() {
        Timer timer = new Timer();
        timer.scheduleAtFixedRate(new IngestTask(), 0, config.getIngestionIntervalMs());
    }

    class IngestTask extends TimerTask {
        @Override
        public void run() {
            try {
                System.out.println("IngestionAgent: Fetching data from source...");
                URL url = new URL(config.getSourceUrl());
                BufferedReader reader = new BufferedReader(new InputStreamReader(url.openStream()));

                StringBuilder rawData = new StringBuilder();
                String line;
                while ((line = reader.readLine()) != null) {
                    rawData.append(line).append("\n");
                }
                reader.close();

                StorageHelper.saveRawData(config.getStorageOutputPath(), rawData.toString());
                System.out.println("IngestionAgent: Data ingested and saved.");
            } catch (Exception e) {
                System.err.println("IngestionAgent: Failed to ingest data: " + e.getMessage());
            }
        }
    }

    /**
     * Standalone entry point for running the IngestionAgent independently.
     */
    public static void main(String[] args) {
        AgentConfig config = new AgentConfig("../config/config.json");
        IngestionAgent agent = new IngestionAgent(config);
        agent.start();
        // Keep the agent running for demonstration (e.g., 1 interval)
        try { Thread.sleep(config.getIngestionIntervalMs() + 2000); } catch (InterruptedException e) {}
    }
}

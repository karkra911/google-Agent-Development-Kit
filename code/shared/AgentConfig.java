package shared;

import java.io.FileReader;
import java.nio.file.Paths;
import java.util.Timer;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

public class AgentConfig {
    private String projectId;
    private String sourceUrl;
    private String storageOutputPath;
    private long ingestionIntervalMs;

    public AgentConfig(String configFilePath) {
        loadConfig(configFilePath);
    }

    private void loadConfig(String path) {
        try (FileReader reader = new FileReader(Paths.get(path).toFile())) {
            JsonObject json = JsonParser.parseReader(reader).getAsJsonObject();
            projectId = json.get("project_id").getAsString();

            JsonObject agents = json.getAsJsonObject("agents");
            JsonObject ingestion = agents.getAsJsonObject("ingestion");

            sourceUrl = ingestion.get("source_url").getAsString();
            long intervalMinutes = ingestion.get("fetch_interval_minutes").getAsLong();
            ingestionIntervalMs = intervalMinutes * 60 * 1000;

            JsonObject storage = json.getAsJsonObject("storage");
            storageOutputPath = storage.get("output_path").getAsString();

        } catch (Exception e) {
            System.err.println("AgentConfig: Failed to load config - " + e.getMessage());
        }
    }

    public String getProjectId() {
        return projectId;
    }

    public String getSourceUrl() {
        return sourceUrl;
    }

    public String getStorageOutputPath() {
        return storageOutputPath;
    }

    public long getIngestionIntervalMs() {
        return ingestionIntervalMs;
    }
}

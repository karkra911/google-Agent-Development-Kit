package agents;

import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.QueryJobConfiguration;
import com.google.cloud.bigquery.TableResult;
import shared.AgentConfig;

/**
 * QueryAgent autonomously retrieves and filters data from BigQuery using a configured query.
 * Usage: Instantiate with AgentConfig and call runQuery().
 */
public class QueryAgent {

    private final AgentConfig config;
    private final BigQuery bigquery;

    public QueryAgent(AgentConfig config) {
        this.config = config;
        this.bigquery = BigQueryOptions.getDefaultInstance().getService();
    }

    public TableResult runQuery() throws InterruptedException {
        String query = config.getQueryTemplate();

        QueryJobConfiguration queryConfig = QueryJobConfiguration.newBuilder(query).build();

        System.out.println("QueryAgent: Executing query...");
        TableResult result = bigquery.query(queryConfig);
        System.out.println("QueryAgent: Query executed successfully.");

        return result;
    }

    /**
     * Standalone entry point for running the QueryAgent independently.
     */
    public static void main(String[] args) throws InterruptedException {
        AgentConfig config = new AgentConfig("../config/config.json");
        QueryAgent agent = new QueryAgent(config);
        agent.runQuery();
    }
}

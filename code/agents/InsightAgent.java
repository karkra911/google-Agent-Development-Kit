package agents;

import com.google.cloud.bigquery.FieldValue;
import com.google.cloud.bigquery.FieldValueList;
import com.google.cloud.bigquery.TableResult;

import java.util.ArrayList;
import java.util.List;

/**
 * InsightAgent autonomously analyzes query results to derive meaningful insights.
 * Usage: Instantiate and call analyze(TableResult).
 */
public class InsightAgent {

    public InsightAgent() {
        // Initialize any resources if needed
    }

    // Example method to analyze trends or perform simple insights on query results
    public List<String> analyze(TableResult queryResult) {
        List<String> insights = new ArrayList<>();

        // Simple example: count number of rows and provide insight
        long rowCount = queryResult.getTotalRows();
        insights.add("Total rows in dataset: " + rowCount);

        // Example: analyze first column values (if numeric)
        // This is just a placeholder for actual analysis logic
        double sum = 0;
        long count = 0;

        for (FieldValueList row : queryResult.iterateAll()) {
            FieldValue val = row.get(0);
            if (val.getValue() instanceof Number) {
                sum += ((Number) val.getValue()).doubleValue();
                count++;
            }
        }

        if (count > 0) {
            double avg = sum / count;
            insights.add("Average value of first column: " + avg);
        } else {
            insights.add("No numeric data found in first column for analysis.");
        }

        return insights;
    }

    /**
     * Standalone entry point for running the InsightAgent independently (demo only).
     */
    public static void main(String[] args) {
        System.out.println("InsightAgent: Please use this agent with a TableResult from QueryAgent.");
    }
}

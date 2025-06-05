package agents;

/**
 * PresentationAgent autonomously presents insights (e.g., logs, reports, dashboards).
 * Usage: Instantiate and call present(List<String> insights).
 */
public class PresentationAgent {

    public PresentationAgent() {
        // Initialize any presentation resources if needed
    }

    // Simple method to display insights to console (can be extended to generate reports)
    public void present(List<String> insights) {
        System.out.println("----- Insights Report -----");
        for (String insight : insights) {
            System.out.println("- " + insight);
        }
        System.out.println("---------------------------");
    }

    /**
     * Standalone entry point for running the PresentationAgent independently (demo only).
     */
    public static void main(String[] args) {
        System.out.println("PresentationAgent: Please use this agent with a list of insights from InsightAgent.");
    }
}

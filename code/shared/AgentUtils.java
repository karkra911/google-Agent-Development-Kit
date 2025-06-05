package shared;

public class AgentUtils {

    // Example utility method for logging
    public static void log(String agentName, String message) {
        System.out.println("[" + agentName + "] " + message);
    }

    // Example utility method for simulating a delay
    public static void wait(int seconds) {
        try {
            Thread.sleep(seconds * 1000);
        } catch (InterruptedException e) {
            System.err.println("Wait interrupted: " + e.getMessage());
        }
    }
}

package shared;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

public class StorageHelper {

    // Save content to file (creates directories if needed)
    public static void saveToFile(String content, String filePath) throws IOException {
        Path path = Paths.get(filePath);
        Files.createDirectories(path.getParent());  // create parent dirs if not exist
        Files.writeString(path, content);
        System.out.println("StorageHelper: Saved file to " + filePath);
    }

    // Read content from file
    public static String readFromFile(String filePath) throws IOException {
        Path path = Paths.get(filePath);
        String content = Files.readString(path);
        System.out.println("StorageHelper: Read file from " + filePath);
        return content;
    }
}

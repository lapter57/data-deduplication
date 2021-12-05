package ru.spbstu.core.storage;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import ru.spbstu.core.file.ByteFile;

import javax.annotation.PostConstruct;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;


@Slf4j
@Component
public class LocalStorage implements Storage {
    @Value("${storage.basePath}")
    private String basePath;

    @PostConstruct
    private void createBasePath() throws IOException {
        Files.createDirectories(Paths.get(basePath));
        log.info("Created {}", basePath);
    }

    @Override
    public void save(ByteFile file, String location) {
        try {
            Files.write(Path.of(basePath, location), file.bytes());
        } catch (IOException e) {
            throw new RuntimeException("Couldn't write file", e);
        }
    }

    @Override
    public ByteFile getFile(String location) {
        try {
            final var bytes = Files.readAllBytes(Path.of(basePath, location));
            return new ByteFile(bytes);
        } catch (IOException e) {
            throw new RuntimeException("Couldn't read file " + location, e);
        }
    }
}

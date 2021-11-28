package ru.spbstu.core.storage;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import ru.spbstu.core.file.ByteFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;


@RequiredArgsConstructor
@Component
public class LocalStorage implements Storage {
    @Value("${storage.basePath}")
    private String basePath;

    @Override
    public boolean connect() {
        return true;
    }

    @Override
    public void disconnect() {

    }

    @Override
    public boolean save(ByteFile file, String location) {
        try {
            Files.write(Path.of(basePath, location), file.bytes());
            return true;
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

    @Override
    public void close() {
        disconnect();
    }
}

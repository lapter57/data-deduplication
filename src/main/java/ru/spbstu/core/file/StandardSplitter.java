package ru.spbstu.core.file;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.List;

@RequiredArgsConstructor
@Component
public class StandardSplitter implements Splitter {
    @Value("${storage.blockSize}")
    private int blockSize;

    @Override
    public List<ByteFile> split(final InputStream stream) throws RuntimeException {
        final var list = new ArrayList<ByteFile>();
        var length = 0L;
        do {
            try {
                list.add(new ByteFile(stream.readNBytes(blockSize)));
                length = stream.skip(blockSize);
            } catch (IOException e) {
                throw new RuntimeException("Couldn't split file", e);
            }
        } while (length == blockSize);
        return list;
    }

    @Override
    public InputStream combine(final List<ByteFile> files) throws RuntimeException {
        final var output = new ByteArrayOutputStream();

        files.forEach(file -> {
            try {
                output.write(file.bytes());
            } catch (IOException e) {
                throw new RuntimeException("Couldn't write to byte array output stream", e);
            }
        });
        try {
            output.flush();
        } catch (IOException e) {
            throw new RuntimeException("Couldn't flush", e);
        }
        return new ByteArrayInputStream(output.toByteArray());
    }
}

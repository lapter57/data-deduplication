package ru.spbstu.core.storage;

import ru.spbstu.core.file.ByteFile;

public interface Storage {
    void save(final ByteFile file, final String location);

    ByteFile getFile(final String location);

}

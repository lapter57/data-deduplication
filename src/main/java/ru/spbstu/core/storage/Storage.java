package ru.spbstu.core.storage;

import ru.spbstu.core.file.ByteFile;

public interface Storage extends Connectable, AutoCloseable {
    boolean save (final ByteFile file, final String location);

    ByteFile getFile(final String location);

}

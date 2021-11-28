package ru.spbstu.core.file;

import java.io.InputStream;
import java.util.List;

public interface Splitter {
    List<ByteFile> split(final InputStream stream) throws RuntimeException;
    InputStream combine(final List<ByteFile> files) throws RuntimeException;
}

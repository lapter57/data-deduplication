package ru.spbstu.core.file;

import java.io.InputStream;
import java.util.List;

public interface Splitter {
    List<ByteFile> split(final InputStream stream);

    InputStream combine(final List<ByteFile> files);
}

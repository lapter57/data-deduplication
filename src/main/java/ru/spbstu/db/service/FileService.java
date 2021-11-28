package ru.spbstu.db.service;

import org.springframework.stereotype.Service;
import ru.spbstu.db.model.File;
import ru.spbstu.db.repo.FileRepository;

@Service
public class FileService extends AbstractEntityService<File, String, FileRepository> {

    protected FileService(final FileRepository repository) {
        super(repository);
    }
}

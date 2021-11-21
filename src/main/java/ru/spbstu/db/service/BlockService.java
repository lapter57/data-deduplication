package ru.spbstu.db.service;

import org.springframework.stereotype.Service;
import ru.spbstu.db.model.Block;
import ru.spbstu.db.repo.BlockRepository;

@Service
public class BlockService extends AbstractEntityService<Block, String, BlockRepository> {

    protected BlockService(final BlockRepository repository) {
        super(repository);
    }
}

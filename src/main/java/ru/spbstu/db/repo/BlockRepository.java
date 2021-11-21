package ru.spbstu.db.repo;

import org.springframework.data.mongodb.repository.ReactiveMongoRepository;
import org.springframework.stereotype.Repository;
import ru.spbstu.db.model.Block;

@Repository
public interface BlockRepository extends ReactiveMongoRepository<Block, String> {
}

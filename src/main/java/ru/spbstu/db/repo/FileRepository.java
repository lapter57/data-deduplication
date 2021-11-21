package ru.spbstu.db.repo;

import org.springframework.data.mongodb.repository.ReactiveMongoRepository;
import org.springframework.stereotype.Repository;
import ru.spbstu.db.model.File;

@Repository
public interface FileRepository extends ReactiveMongoRepository<File, Long> {
}

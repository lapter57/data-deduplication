package ru.spbstu.db.repo;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;
import ru.spbstu.db.model.File;

@Repository
public interface FileRepository extends MongoRepository<File, String> {
}

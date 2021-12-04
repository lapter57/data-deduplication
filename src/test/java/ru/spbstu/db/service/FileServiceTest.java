package ru.spbstu.db.service;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.containers.MongoDBContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.utility.DockerImageName;
import reactor.test.StepVerifier;
import ru.spbstu.db.model.File;

import java.util.List;

@SpringBootTest
@Testcontainers
class FileServiceTest {

    @Container
    private static final MongoDBContainer MONGO_DB = new MongoDBContainer(DockerImageName.parse("mongo:bionic"));

    @DynamicPropertySource
    static void mongoProperties(final DynamicPropertyRegistry registry) {
        MONGO_DB.start();
        registry.add("spring.data.mongodb.uri", MONGO_DB::getReplicaSetUrl);
    }

    @Autowired
    private FileService fileService;

    @Test
    void testInsertFile() {
//        final var file = new File("1", List.of("hash1", "hash2"), "image/png");
//        StepVerifier.create(fileService.insert(file))
//                .expectNext(file)
//                .expectComplete()
//                .verify();
    }

    @Test
    void testFindFileById() {
//        final var file = fileService.insert(new File("1", List.of("hash1", "hash2"), "image/png")).block();
//        fileService.insert(new File("2", List.of("hash3"), "image/jpeg")).block();
//        StepVerifier.create(fileService.findById(file.id()))
//                .expectNext(file)
//                .expectComplete()
//                .verify();
    }
}

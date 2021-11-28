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
import ru.spbstu.db.model.Block;

@SpringBootTest
@Testcontainers
class BlockServiceTest {

    @Container
    private static final MongoDBContainer MONGO_DB = new MongoDBContainer(DockerImageName.parse("mongo:bionic"));

    @DynamicPropertySource
    static void mongoProperties(final DynamicPropertyRegistry registry) {
        MONGO_DB.start();
        registry.add("spring.data.mongodb.uri", MONGO_DB::getReplicaSetUrl);
    }

    @Autowired
    private BlockService blockService;

    @Test
    void testInsertBlock() {
        final var block = new Block("qwerty", "./block_1");
//        StepVerifier.create(blockService.insert(block))
//                .expectNext(block)
//                .expectComplete()
//                .verify();
    }

    @Test
    void testFindBlockById() {
        final var block = blockService.insert(new Block("block1", "./block_1"));
        blockService.insert(new Block("block2", "./block_2"));
        blockService.findById(block.hash());
//                .expectNext(block)
//                .expectComplete()
//                .verify();
    }
}

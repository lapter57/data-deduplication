package ru.spbstu.core.controller;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.tuple.Pair;
import org.springframework.core.io.InputStreamResource;
import org.springframework.core.io.Resource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import ru.spbstu.core.file.ByteFile;
import ru.spbstu.core.file.Splitter;
import ru.spbstu.core.hash.HashConverter;
import ru.spbstu.core.storage.Storage;
import ru.spbstu.db.model.Block;
import ru.spbstu.db.model.File;
import ru.spbstu.db.service.BlockService;
import ru.spbstu.db.service.FileService;

import java.io.IOException;
import java.net.URI;
import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.concurrent.*;
import java.util.stream.Collectors;

@Slf4j
@RestController
@RequiredArgsConstructor
public class FileController {

    private static final String DEFAULT_CONTENT_TYPE = "application/octet-stream";
    private static final Executor EXECUTOR = Executors.newFixedThreadPool(
            Runtime.getRuntime().availableProcessors() + 1);

    private final Storage storage;
    private final Splitter splitter;
    private final BlockService blockService;
    private final FileService fileService;
    private final HashConverter hashConverter;

    @PostMapping(value = "/file", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @ResponseBody
    public ResponseEntity<String> uploadFile(@RequestPart("file") MultipartFile file)
            throws IOException, ExecutionException, InterruptedException, TimeoutException {
        final var parts = splitter.split(file.getInputStream());
        final var hashes = parts.stream()
                .map(byteFile -> Pair.of(hashConverter.toHash(byteFile.bytes()), byteFile))
                .toList();

        final var hashToBytes = hashes.stream()
                .collect(Collectors.toMap(Pair::getKey, Pair::getValue, (bf1, bf2) -> bf1));

        final var futures = hashToBytes.entrySet().stream()
                .map(entry -> CompletableFuture.runAsync(() -> handleWrite(entry), EXECUTOR))
                .toList();

        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).get(1, TimeUnit.HOURS);

        final var contentType = Optional.ofNullable(file.getContentType()).orElse(DEFAULT_CONTENT_TYPE);

        final var id = saveFileToDB(hashes.stream().map(Pair::getKey).toList(), contentType);

        log.debug("Saved file: id = {} ; mime = {}", id, contentType);

        return ResponseEntity.created(URI.create(id)).body(id);
    }

    @GetMapping(value = "/file/{id}")
    @ResponseBody
    public ResponseEntity<Resource> downloadFile(@PathVariable("id") String fileId) throws IOException {
        final var fileOptional = fileService.findById(fileId);
        if (fileOptional.isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        final var file = fileOptional.get();
        final var resultFile = splitter.combine(
                file.hashes().stream()
                        .map(storage::getFile)
                        .collect(Collectors.toList()));
        return ResponseEntity.ok()
                .contentLength(resultFile.available())
                .contentType(MediaType.valueOf(file.mimeType()))
                .body(new InputStreamResource(resultFile));
    }

    private void handleWrite(final Map.Entry<String, ByteFile> tuple) {
        blockService.findById(tuple.getKey()).ifPresentOrElse(ign -> {
        }, () -> {
            storage.save(tuple.getValue(), tuple.getKey());
            blockService.insert(new Block(tuple.getKey(), tuple.getKey()));
        });
    }

    private String saveFileToDB(final List<String> hashes, String mimeType) {
        return fileService.insert(new File(null, hashes, mimeType)).id();
    }

}

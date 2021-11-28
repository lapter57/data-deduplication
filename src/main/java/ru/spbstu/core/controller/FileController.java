package ru.spbstu.core.controller;

import lombok.RequiredArgsConstructor;
import org.apache.commons.collections4.ListUtils;
import org.apache.commons.lang3.tuple.Pair;
import org.springframework.core.io.InputStreamResource;
import org.springframework.core.io.Resource;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestPart;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;
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
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;
import java.util.stream.Collectors;

@RestController
@RequiredArgsConstructor
public class FileController {

    private final Storage storage;
    private final Splitter splitter;
    private final BlockService blockService;
    private final FileService fileService;
    private final HashConverter hashConverter;

    @PostMapping(value = "/file", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @ResponseBody
    public ResponseEntity<String> uploadFile(
            @RequestPart("file") MultipartFile file) throws IOException, ExecutionException, InterruptedException, TimeoutException {
        final var parts = splitter.split(file.getInputStream());
        final var hashes = parts.stream()
                .map(byteFile -> Pair.of(hashConverter.toHash(byteFile.bytes()), byteFile))
                .toList();

        final var processes = getProcesses();
        final var map = new HashMap<String, ByteFile>();
        hashes.forEach(pair -> map.putIfAbsent(pair.getKey(), pair.getValue()));
        final var futures = map.entrySet().stream()
                .map(entry -> CompletableFuture.runAsync(()->handleWrite(entry), Executors.newFixedThreadPool(processes)))
                .toList();

        var cf = CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]));
        cf.get(1, TimeUnit.HOURS);

        final var id = saveFileToDB(hashes.stream().map(Pair::getKey).toList(), file.getContentType());
        return ResponseEntity.created(URI.create(id)).body(id);
    }

    @GetMapping(value = "/file/{id}")
    @ResponseBody
    public ResponseEntity<Resource> downloadFile(@PathVariable("id") String fileId) throws IOException {
        final var file = fileService.findById(fileId);
        if (file.isEmpty()) {
            return ResponseEntity.notFound().build();
        }
        final var fileRecord = file.get();
        final var resultFile = splitter.combine(
                fileRecord.hashes().stream()
                        .map(storage::getFile)
                        .collect(Collectors.toList()));
        return ResponseEntity.ok()
                .contentLength(resultFile.available())
                .contentType(MediaType.valueOf(fileRecord.mimeType()))
                .body(new InputStreamResource(resultFile));
    }

    private static int getProcesses() {
        return Runtime.getRuntime().availableProcessors() + 1;
    }

    private void handleWrite(final Map.Entry<String, ByteFile> tuple) {
        blockService.findById(tuple.getKey()).ifPresentOrElse(ign -> {
        }, () -> {
            storage.connect();
            try (storage) {
                storage.save(tuple.getValue(), tuple.getKey());
                blockService.insert(new Block(tuple.getKey(), tuple.getKey()));
            } catch (Exception e) {
                throw new RuntimeException("Unbelievable", e);
            }
        });
    }


    private String saveFileToDB(final List<String> hashes, String mimeType) {
        return fileService.insert(new File(null, hashes, mimeType)).id();
    }

}

package ru.spbstu.core.controller;

import lombok.RequiredArgsConstructor;
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
import java.util.List;
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
            @RequestPart("file") MultipartFile file) throws IOException {
        final var hashes = splitter.split(file.getInputStream()).stream()
                .map(this::saveSubFile)
                .collect(Collectors.toList());
        final var id = saveData(hashes, file.getContentType());
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

    private String saveSubFile(final ByteFile file) {
        final var hash = hashConverter.toHash(file.bytes());
        blockService.findById(hash).ifPresentOrElse(ign -> {
        }, () -> {
            storage.connect();
            try (storage) {
                storage.save(file, hash);
                blockService.insert(new Block(hash, hash));
            } catch (Exception e) {
                throw new RuntimeException("Unbelievable", e);
            }
        });
        return hash;
    }

    private String saveData(final List<String> hashes, String mimeType) {
        return fileService.insert(new File(null, hashes, mimeType)).id();
    }

}

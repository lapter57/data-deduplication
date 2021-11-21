package ru.spbstu.db.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import java.util.List;

@Document(collection = "files")
public record File(@Id Long id,
                   List<String> hashes,
                   String mimeType) {
}

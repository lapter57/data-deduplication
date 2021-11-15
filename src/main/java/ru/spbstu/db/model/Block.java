package ru.spbstu.db.model;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

@Document(collection = "blocks")
public record Block(@Id String hash,
                    String location) {
}

package ru.spbstu.core.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class StatusController {

    @GetMapping("/status")
    @ResponseBody
    public ResponseEntity<String> handleStatus() {
        return ResponseEntity.ok("Online");
    }
}

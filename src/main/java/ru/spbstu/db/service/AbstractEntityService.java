package ru.spbstu.db.service;

import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import org.springframework.data.repository.reactive.ReactiveCrudRepository;
import reactor.core.publisher.Mono;

@RequiredArgsConstructor(access = AccessLevel.PROTECTED)
public abstract class AbstractEntityService<E, K, R extends ReactiveCrudRepository<E, K>> {

    protected final R repository;

    public Mono<E> insert(final E entity) {
        return repository.save(entity);
    }

    public Mono<E> findById(final K id) {
        return repository.findById(id);
    }
}

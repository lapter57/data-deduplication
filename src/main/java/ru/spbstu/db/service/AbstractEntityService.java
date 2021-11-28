package ru.spbstu.db.service;

import lombok.AccessLevel;
import lombok.RequiredArgsConstructor;
import org.springframework.data.repository.CrudRepository;

import java.util.Optional;

@RequiredArgsConstructor(access = AccessLevel.PROTECTED)
public abstract class AbstractEntityService<E, K, R extends CrudRepository<E, K>> {

    protected final R repository;

    public E insert(final E entity) {
        return repository.save(entity);
    }

    public Optional<E> findById(final K id) {
        return repository.findById(id);
    }
}

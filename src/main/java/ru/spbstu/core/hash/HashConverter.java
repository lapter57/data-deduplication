package ru.spbstu.core.hash;

import com.google.common.hash.HashFunction;
import com.google.common.hash.Hashing;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;
import org.springframework.util.Base64Utils;

import java.util.Arrays;

@Component
public class HashConverter {
    private final Hashes hash;

    @Autowired
    public HashConverter(@Value("${storage.hashType}") final String hashType) {
        this.hash = Hashes.from(hashType);

    }

    public String toHash(byte[] array) {
        return Base64Utils.encodeToUrlSafeString(hash.hashFunction.hashBytes(array).asBytes());
    }

    private enum Hashes {
        SHA_256("sha-256", Hashing.sha256()),
        SHA_512("sha-512", Hashing.sha512()),
        MURMUR3_128("murmur3-128", Hashing.murmur3_128()),
        ADLER_32("adler-32", Hashing.adler32());

        private final HashFunction hashFunction;
        private final String name;

        Hashes(final String name, final HashFunction hashFunction) {
            this.name = name;
            this.hashFunction = hashFunction;
        }

        static Hashes from(final String name) {
            return Arrays.stream(Hashes.values())
                    .filter(hash -> hash.name.equals(name.toLowerCase()))
                    .findFirst()
                    .orElseThrow(() -> new IllegalArgumentException(String.format("Hash function %s doesn't exists", name)));
        }
    }
}

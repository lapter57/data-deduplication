package ru.spbstu.config;

import org.springframework.context.annotation.Bean;
import org.springframework.security.config.annotation.web.reactive.EnableWebFluxSecurity;
import org.springframework.security.config.web.server.ServerHttpSecurity;
import org.springframework.security.web.server.SecurityWebFilterChain;
import org.springframework.security.web.server.savedrequest.NoOpServerRequestCache;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.reactive.CorsWebFilter;
import org.springframework.web.cors.reactive.UrlBasedCorsConfigurationSource;

import java.util.Collections;

import static org.springframework.security.config.web.server.SecurityWebFiltersOrder.CORS;

@EnableWebFluxSecurity
public class WebSecurityConfig {

    @Bean
    public SecurityWebFilterChain securityWebFilterChain(final ServerHttpSecurity http,
                                                         final CorsWebFilter corsWebFilter) {
        return http.httpBasic().disable()
                .formLogin().disable()
                .logout().disable()
                .headers().disable()
                .csrf().disable()
                .requestCache(cache -> cache
                        .requestCache(NoOpServerRequestCache.getInstance()))
                .authorizeExchange(exchanges -> exchanges
                        .anyExchange().permitAll())
                .addFilterAt(corsWebFilter, CORS)
                .build();
    }

    @Bean
    public CorsWebFilter corsWebFilter() {
        final var corsConfig = new CorsConfiguration();
        corsConfig.setAllowedOriginPatterns(Collections.singletonList(CorsConfiguration.ALL));
        corsConfig.addAllowedMethod(CorsConfiguration.ALL);
        corsConfig.addAllowedHeader(CorsConfiguration.ALL);
        corsConfig.setAllowCredentials(true);

        final var source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", corsConfig);

        return new CorsWebFilter(source);
    }
}

FROM gradle:jdk17 AS build
WORKDIR /app
COPY . /app
RUN gradle bootJar --no-daemon

FROM openjdk:17-alpine
RUN apk update && apk add coreutils
COPY --from=build /app/build/libs/*.jar app.jar
ENTRYPOINT ["java", "-jar","/app.jar"]

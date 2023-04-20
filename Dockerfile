FROM openjdk:11-alpine
ENTRYPOINT ["/usr/bin/airbusspringone.sh"]

COPY airbusspringone.sh /usr/bin/airbusspringone.sh
COPY target/airbusspringone.jar /usr/share/airbusspringone/airbusspringone.jar

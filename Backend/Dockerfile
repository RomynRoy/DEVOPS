#FROM openjdk:11
# TODO: Add the compiled java (aka bytecode, aka .class)
# TODO: Run the Java with: “java Main” command.
#COPY Main.java /usr/src/app/
#CMD cd /usr/src/app/ ; javac Main.java
#CMD cd /usr/src/app/ ; java Main.java

# Build
FROM maven:3.6.3-jdk-11 AS myapp-build
ENV MYAPP_HOME /opt/myapp
WORKDIR $MYAPP_HOME
COPY simple-api2/pom.xml .
COPY simple-api2/src ./src
RUN mvn package -DskipTests
# Run
FROM openjdk:11-jre
ENV MYAPP_HOME /opt/myapp
WORKDIR $MYAPP_HOME
COPY --from=myapp-build $MYAPP_HOME/target/*.jar $MYAPP_HOME/myapp.jar
ENTRYPOINT java -jar myapp.jar

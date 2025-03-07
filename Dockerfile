FROM bitnami/spark:3.5.1

USER root

# Install system packages and add MongoDB repository
RUN apt-get update && apt-get install -y python3-pip curl iputils-ping gnupg \
    && curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | gpg --dearmor -o /usr/share/keyrings/mongodb-server-8.0.gpg \
    && echo "deb [ signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] http://repo.mongodb.org/apt/debian bookworm/mongodb-org/8.0 main" | tee /etc/apt/sources.list.d/mongodb-org-8.0.list \
    && apt-get update && apt-get install -y mongodb-mongosh

# Upgrade pip and install Python dependencies
RUN pip3 install --upgrade pip
RUN pip3 install requests kafka-python pyspark==3.5.1 pymongo cassandra-driver streamlit

# Create directory for Spark jars
RUN mkdir -p /opt/spark/jars

# Download MongoDB Spark Connector and other dependencies
RUN curl -o /opt/spark/jars/mongo-spark-connector_2.12-10.3.0.jar https://repo1.maven.org/maven2/org/mongodb/spark/mongo-spark-connector_2.12/10.3.0/mongo-spark-connector_2.12-10.3.0.jar
RUN curl -o /opt/spark/jars/guava-32.0.1-jre.jar https://repo1.maven.org/maven2/com/google/guava/guava/32.0.1-jre/guava-32.0.1-jre.jar
RUN curl -o /opt/spark/jars/scala-library-2.12.18.jar https://repo1.maven.org/maven2/org/scala-lang/scala-library/2.12.18/scala-library-2.12.18.jar

# Set working directory and copy application code
WORKDIR /app
COPY . /app

# Default command
CMD ["python3"]
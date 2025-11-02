# Use an official openpolicyagent runtime as a parent image
FROM openpolicyagent/opa:1.10.0

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Make port 8181 available to the world outside this container
EXPOSE 8181

# Run app.py when the container launches
CMD ["run", "-s", "rego/user.rego", "-l", "debug"]

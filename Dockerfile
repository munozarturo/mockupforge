# Use a base image with Fedora
FROM fedora:latest

# Install necessary packages
RUN dnf update -y && \
    dnf install -y gimp python3 python3-pip && \
    dnf clean all

# Copy the Flask application code into the container
COPY . /app
WORKDIR /app

# Create a directory for temporary files
RUN mkdir -p temp

# Install Flask and any other Python dependencies
RUN pip3 install flask python-dotenv boto3

# Create the GIMP plug-ins directory if it doesn't exist
RUN mkdir -p ~/.config/GIMP/2.10/plug-ins

# Copy the contents of GIMP plug-ins to the GIMP plug-ins folder
RUN cp -r ./gimp/plug-ins/* ~/.config/GIMP/2.10/plug-ins/

# Set the permissions for the copied scripts
RUN chmod +x ~/.config/GIMP/2.10/plug-ins/*

# Expose the Flask port
EXPOSE 5000

# Run the Flask application
CMD ["python3", "app.py"]
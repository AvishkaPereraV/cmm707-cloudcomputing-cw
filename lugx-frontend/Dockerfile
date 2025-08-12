# Use the official NGINX base image
FROM nginx:alpine

RUN rm -rf /usr/share/nginx/html/*

# Copy all static Lugx files into the NGINX web directory
COPY . /usr/share/nginx/html

# Copy the nginx config
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80


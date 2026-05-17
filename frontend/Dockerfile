# frontend/Dockerfile
FROM nginx:alpine

# Copy index.html as a template
COPY index.html /usr/share/nginx/html/index.html.template

# Use envsubst to replace BACKEND_URL in index.html at runtime
# Default BACKEND_URL if not provided
ENV BACKEND_URL=http://localhost:8080

CMD ["/bin/sh", "-c", "envsubst '${BACKEND_URL}' < /usr/share/nginx/html/index.html.template > /usr/share/nginx/html/index.html && exec nginx -g 'daemon off;'"]

EXPOSE 80

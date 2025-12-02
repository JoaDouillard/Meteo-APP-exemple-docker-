# Utilise l'image Nginx officielle
FROM nginx:alpine

# Copier la configuration Nginx personnalisée
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copier les fichiers HTML
COPY index.html /usr/share/nginx/html/

# Exposer le port 80
EXPOSE 80

# Nginx se lance automatiquement avec l'image

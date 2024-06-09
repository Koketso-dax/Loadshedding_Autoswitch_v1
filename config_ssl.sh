sudo certbot certonly --standalone -d web-01.koketsodiale.tech
sudo certbot certonly --standalone -d web-02.koketsodiale.tech

sudo bash -c 'cat > /etc/nginx/sites-available/default' << EOF
server {
    listen 80;
    server_name web-01.koketsodiale.tech;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name web-01.koketsodiale.tech;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:8080; # Or the port your app runs on
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# test config
sudo nginx -t
sudo systemctl reload nginx

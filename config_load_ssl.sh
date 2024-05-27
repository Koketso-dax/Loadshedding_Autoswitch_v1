sudo certbot certonly --standalone -d koketsodiale.tech -d www.koketsodiale.tech

sudo bash -c 'cat > /etc/haproxy/haproxy.cfg' << EOF
frontend https-in
    bind *:443 ssl crt /etc/haproxy/certs/koketsodiale.tech.pem
    mode http
    default_backend webservers

backend webservers
    mode http
    balance roundrobin
    option forwardfor
    http-request set-header X-Forwarded-Proto https
    server web01 web-01:443 ssl verify none
    server web02 web-02:443 ssl verify none
EOF

# Test !
sudo haproxy -f /etc/haproxy/haproxy.cfg -c
sudo systemctl reload haproxy

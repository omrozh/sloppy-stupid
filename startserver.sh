apt install python3
apt install python3-pip
apt install nginx
apt install gunicorn

printf "server {\nlisten 80;\nserver_name 192.0.2.0;\n\nlocation / {\nproxy_pass http://127.0.0.1:8000;\nproxy_set_header Host \$host;\nproxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;\n}\n}" >> "/etc/nginx/sites-enabled/nginx-config"

nginx -s reload
pip3 install -r requirements.txt
gunicorn -w 3 app:app

apt-get remove certbot
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
sudo certbot certonly --nginx

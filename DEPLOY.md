# Deployment notes for raspbian

## Raspbian

Default credentials:
- username: pi
- password: raspberry

Enable debian testing: Replace `stable` (or `stretch` etc.) with
`testing` (or `buster`) in `/etc/apt/sources.list`.

    sudo apt update && sudo apt dist-upgrade
    sudo apt install vim neovim git tmux zsh tree
    chsh -s /bin/zsh

## Setup network

- Give static IP

https://www.electronicshub.org/setup-static-ip-address-raspberry-pi/

    /etc/dhcpcd.conf
    ----------------
    interface eth0
    static ip_address=192.168.1.77/24
    static routers=192.168.1.1
    static domain_name_servers=192.168.1.1 8.8.8.8 fd51:42f8:caae:d92e::1

    sudo systemctl restart dhcpcd

## Setup ssh

Enable ssh: https://www.raspberrypi.org/documentation/remote-access/ssh/

    sudo systemctl enable --now ssh

Copy public ssh key:

    ssh-copy-id pi@192.168.1.77

or:

    scp ~/.ssh/id_rsa.pub pi@192.168.1.77:
    ssh pi@192.168.1.77
    mkdir .ssh
    cat id_rsa.pub > .ssh/authorized_keys

Generate ssh key on raspberrypi:

    ssh-keygen -t rsa -b 4096

Add key at https://gitlab.com/profile/keys

Secure server:

https://plusbryan.com/my-first-5-minutes-on-a-server-or-essential-security-for-linux-servers

    /etc/ssh/sshd_config
    --------------------
    PasswordAuthentication no
    PermitRootLogin no
    Port ...

    sudo systemctl restart ssh

## Setup duckdns

https://www.duckdns.org/install.jsp?tab=linux-cron&domain=buzuki

## Setup buzuki

    sudo apt install python3-venv python3-pip

    git clone git@gitlab.com:forkbong/buzuki.git
    cd buzuki
    python3 -m venv venv
    source venv/bin/activate
    pip3 install -r requirements.txt

## Setup redis

    sudo apt install redis
    sudo systemctl enable --now redis-server

    /etc/hosts
    ----------
    127.0.0.1	redis

## Configure nginx

    sudo apt install nginx certbot python-certbot-nginx
    sudo certbot --nginx -d buzuki.duckdns.org
    sudo cp nginx/nginx.conf /etc/nginx/sites-available/buzuki
    cd /etc/nginx/sites-enabled/
    sudo rm default
    sudo ln -s /etc/nginx/sites-available/buzuki .
    sudo systemctl enable --now nginx

    sudo certbot renew

## Cross compile buzuki-search

    yay -S cross-git
    sudo systemctl start docker
    cross build --target=armv7-unknown-linux-gnueabihf --release
    scp target/armv7-unknown-linux-gnueabihf/release/buzuki-search pi:

## Troubleshooting

### Network is unreachable

https://raspberrypi.stackexchange.com/a/14107
https://raspberrypi.stackexchange.com/questions/39785

    sudo route -n
    sudo route add default gw 192.168.1.1

### Fan connection

https://raspberrypi.stackexchange.com/a/29692

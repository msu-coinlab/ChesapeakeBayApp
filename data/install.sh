#!/bin/bash
#export DEBIAN_FRONTEND=noninteractive
#wget -O- http://repo.mysql.com/RPM-GPG-KEY-mysql-2022 | gpg --dearmor | tee /usr/share/keyrings/mysql.gpg
#echo 'deb [signed-by=/usr/share/keyrings/mysql.gpg] http://repo.mysql.com/apt/debian bullseye mysql-8.0' | tee /etc/apt/sources.list.d/mysql.list
#echo 'deb [signed-by=/usr/share/keyrings/mysql.gpg] http://repo.mysql.com/apt/debian bullseye mysql-tools' | tee -a /etc/apt/sources.list.d/mysql.list
#echo 'deb-src [signed-by=/usr/share/keyrings/mysql.gpg] http://repo.mysql.com/apt/debian bullseye mysql-tools' | tee -a /etc/apt/sources.list.d/mysql.list
 apt update
 apt install mysql-community-server -y
 systemctl enable mysqld
 systemctl start mysqld

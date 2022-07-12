# vitinhso.com
Step1:
	docker run -d -e POSTGRES_USER=odoo15 -e POSTGRES_PASSWORD=odoo15 -e POSTGRES_DB=postgres --name db15 postgres:10
Step2:
	docker build -t odooc .

Step3:
	docker run -v /home/myaddons:/mnt/extra-addons -p 8069:8069 --name odoo15 --link db15:db odooc



******* 
Cài đặt các thư viện ngoài ở trong file Dockerfile, nhớ cài pip3 trước
nhớ thay đổi đường dẫn path cho myaddons

# vitinhso.com


Step1:
	docker run -d -e POSTGRES_USER=odoo15 -e POSTGRES_PASSWORD=odoo15 -e POSTGRES_DB=postgres --name db15 postgres:10

Step2:
	docker run -v /e/odoo/vitinhsocom:/mnt/extra-addons -p 8069:8069 --name odoo15 --link db15:db odoo:15
----------------
Library requiment
	dropbox

INSTALL MODULE
	web_responsive
	sale_management
	purchase
	stock
	mrp
	hr
	product_warehouse_quantity
	website
	website_blog
	website_sale
	im_livechat
	rowno_in_tree
	contacts
	hr_contract
	prt_report_attachment_preview
	barcode_scanning_sale_purchase
	auto_database_backup (requiment lib 'dropbox')
	custom_b2c

#Auto start bash in ubuntu
crontab -e
add code below:
@reboot /odoo/bash/run_odoo.sh

run_odoo.sh  code
	#!/bin/bash
	sudo -u odoo bash -c 'bash /odoo/bash/odoo.sh'

odoo.sh code
	#!/bin/bash
	cd /odoo/odoo-server
	./odoo-bin -c /etc/odoo-server.conf

# odoo.conf
[options]
addons_path = /opt/odoo/addons
admin_passwd = $pbkdf2-sha512$25000$wvg/J4QwJsS4l1KqFYKQ8g$MzyA19w4aj/2Y.z2ZE1pw.oX.dnfP6U7cRrB2nSJxyeQKMmH/qsLuU.7MzPfGo/xrZskkY1dEwiksbJzj9RlkQ
csv_internal_sep = ,
data_dir = /home/lvquy/.local/share/Odoo
db_host = False
db_maxconn = 64
db_name = False
db_password = False
db_port = False
db_sslmode = prefer
db_template = template0
db_user = odoo
dbfilter = 
demo = {}
email_from = False
from_filter = False
geoip_database = /usr/share/GeoIP/GeoLite2-City.mmdb
http_enable = True
http_interface = 
http_port = 8069
import_partial = 
limit_memory_hard = 2684354560
limit_memory_soft = 2147483648
limit_request = 8192
limit_time_cpu = 60
limit_time_real = 120
limit_time_real_cron = -1
list_db = True
log_db = False
log_db_level = warning
log_handler = :INFO
log_level = info
logfile = 
longpolling_port = 8072
max_cron_threads = 2
osv_memory_age_limit = False
osv_memory_count_limit = False
pg_path = 
pidfile = 
proxy_mode = False
reportgz = False
screencasts = 
screenshots = /tmp/odoo_tests
server_wide_modules = base,web
smtp_password = False
smtp_port = 25
smtp_server = localhost
smtp_ssl = False
smtp_ssl_certificate_filename = False
smtp_ssl_private_key_filename = False
smtp_user = False
syslog = False
test_enable = False
test_file = 
test_tags = None
transient_age_limit = 1.0
translate_modules = ['all']
unaccent = False
upgrade_path = 
without_demo = False
workers = 0
---------
auto start bash on ubuntu
create file: auto.sh
	#!/bin/bash
	sudo -H -u odoo bash -c '/odoo/bash/odoo.sh'
create file: odoo.sh
	#!/bin/bash
	#sudo su - odoo -s /bin/bash
	cd /odoo/odoo-server
	./odoo-bin -c /etc/odoo-server.conf
crontab -e
	@reboot /odoo/bash/odoo.sh

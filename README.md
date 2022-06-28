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
	website
	website_blog
	website_sale
	im_livechat
	purchase
	stock
	mrp
	hr
	product_warehouse_quantity
	rowno_in_tree
	contacts
	hr_contract
	prt_report_attachment_preview
	barcode_scanning_sale_purchase
	auto_database_backup (requiment lib 'dropbox')
	custom_b2c


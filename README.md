# SoftwareEngFinalProject
Gabriel Bernardes-Louis, Tayln Novotney, and Noah DeSousa Software Engineering Final Project. This project is a mobile ordering system for a cafe with some inventory tracking integrated into the software for management and ordering purposes. 

# Database - 
The database utilizes sqlite3, a built in python library for in-memory databases, allowing for easy serverless database utilization. 

Included in this database are the following tables: 
## Categories -
id (primary key)  
name  

## Ingredients - 
id (primary key)  
name  
category_id  
unit  
stock_qty  
reorder_level  
category_id (foreign key to primary key relationship on categories.id)  

## Products -
id (primary key)  
name  
category_id (foreign key to primary key relationship on categories.id)  
price  
is_active  
category_id  

## Product_Ingredients - 
id (primary key)  
product_id (foreign key to primary key relationship on products.id)  
ingredient_id (foreign key to primary key relationship on ingredients.id)  
qty_required  

## Orders - 
id (primary key)  
created_at  
total_price  
status  

## Order_Items - 
id (primary key)  
order_id (foreign key to primary key relationship on orders.id)   
product_id (foreign key to primary key relationship on products.id)  
quantity  
unit_price  


### Note: Not all of these are in use for the purpose of the MVP presentation.


Sprint Week 1 Doc: https://docs.google.com/document/d/14mLJaFsZXAS3qj4s3aCTouInXwaFU6izfTYI6VRuM98/edit?usp=sharing

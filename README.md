# SoftwareEngFinalProject
Gabriel Bernardes-Louis, Tayln Novotney, and Noah DeSousa Software Engineering Final Project. This project is a mobile ordering system for a cafe with some inventory tracking integrated into the software for management and ordering purposes. 

# Database
The database utilizes sqlite3, a built-in Python library for in-memory databases, allowing for easy serverless database utilization.

Included in this database are the following tables:

## Drinks
id (primary key)  
name  
base_price  
is_active  

## Sizes
id (primary key)  
name  
price_add  
default_shots  

## Milks
id (primary key)  
name  

## Flavors
id (primary key)  
name  

## Addons
id (primary key)  
name  
price  

## Categories
id (primary key)  
name  

## Orders
id (primary key)  
created_at  
subtotal  
tax_rate  
tax_amount  
total_price  
status  

## Order_Items
id (primary key)  
order_id (foreign key to primary key relationship on orders.id)  
drink_id (foreign key to primary key relationship on drinks.id)  
size_id (foreign key to primary key relationship on sizes.id)  
milk_id (foreign key to primary key relationship on milks.id)  
flavor_id (foreign key to primary key relationship on flavors.id)  
shots  
temp  
notes  
unit_price  

## Order_Item_Addons
id (primary key)  
order_item_id (foreign key to primary key relationship on order_items.id)  
addon_id (foreign key to primary key relationship on addons.id)


# Orders - 
The orders page displays all orders that are kept in the database, with a flag that marks each as completed/incomplete. This allows for analytics and other auxillary use cases for the information gathered from customers and purchases.


### Build Command: 
streamlit run app/POSapp.py

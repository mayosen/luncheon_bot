from models import db


"""
SELECT SETVAL('"order_id_seq"', (SELECT MAX(id) FROM "order"));
SELECT SETVAL('"orderitem_id_seq"', (SELECT MAX(id) FROM orderitem));
SELECT SETVAL('"product_id_seq"', (SELECT MAX(id) FROM product));
"""

db.execute_sql('SELECT SETVAL(\'"order_id_seq"\', (SELECT MAX(id) FROM \"order\"));')
db.execute_sql('SELECT SETVAL(\'"orderitem_id_seq"\', (SELECT MAX(id) FROM orderitem));')
db.execute_sql('SELECT SETVAL(\'"product_id_seq"\', (SELECT MAX(id) FROM product));')

import psycopg2
import re
import random
from amazon_product_api import CREDENTIALS
import amazonproduct
api = amazonproduct.API(cfg=CREDENTIALS)
def connect():
    """Connect to the PostgreSQL database.
    Returns a database connection."""
    pg = psycopg2.connect("dbname = catalog")
    c = pg.cursor()
    return pg, c


def execute_query(query, variables=()):
    pg, c = connect()
    try:
        c.execute(query, variables)
    except psycopg2.IntegrityError:
        pg.rollback()
        pg.close()
        return
    if re.match("(^INSERT|^UPDATE|^DELETE)", query, re.I) is not None:
        pg.commit()
        pg.close()
    else:
        fetch = c.fetchall()
        pg.close()
        return fetch


def get_category_id(c):
    try:
        result = execute_query("""SELECT id from categories WHERE name = %s""",
                               (c,))
        return result[0][0]
    except IndexError:
        return False


def get_categories():
    return execute_query("SELECT name FROM all_categories")


def get_random_item(int=1):
    arr = execute_query("""
                    SELECT * FROM items
                    """)
    random.shuffle(arr)
    return arr[0:int]

def query_item(ain):
    image = api.item_lookup(ain, ResponseGroup="Images").Items.Item.LargeImage
    # details = api.item_lookup(ain)
    return image
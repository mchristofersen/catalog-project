import psycopg2
import re
import random
from amazon_product_api import CREDENTIALS
import amazonproduct
api = amazonproduct.API(cfg=CREDENTIALS)
def connect():
    """Connect to the PostgreSQL database.
    Returns a database connection."""
    pg = psycopg2.connect(dbname = 'catalogapp',
                          user='postgres',
                          password='Michael1',
                          host='catalogapp.csclhe4v5cyl.us-west-2.rds.amazonaws.com')
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
                    select * from items offset random() * (select count(*) from items) limit 1 ;
                    """)
    random.shuffle(arr)
    return arr[0:int]

def get_med_img(ain):
    try:
        image = api.item_lookup(ain, ResponseGroup="Images")
        image = image.Items.Item.MediumImage.URL.text.encode('utf-8')
        execute_query("UPDATE items SET image=%s WHERE AIN=%s",
                      (image, ain,))
        return ''.join(image)
    except AttributeError:
        get_image(ain)

def get_image(ain):
    try:
        image = api.item_lookup(ain, ResponseGroup="Images")
        image = image.Items.Item.LargeImage.URL
        execute_query("UPDATE items SET image=%s WHERE AIN=%s",
                      (str(image), ain,))
        # details = api.item_lookup(ain)
        return image
    except AttributeError:
        return None


def get_attributes(item):
    try:
        if item[4] is not None:
            res = api.item_lookup(item[2], ResponseGroup="OfferSummary" )
            try:
                price = res.Items.Item.OfferSummary.LowestNewPrice.FormattedPrice
            except AttributeError:
                return get_attributes(list(get_random_item()[0][0:5]))
            item.append(price)
            print item
            return item
        else:
            res = api.item_lookup(item[2], ResponseGroup="Images, OfferSummary" )
            image = res.Items.Item.MediumImage.URL
            item[4]=image
            try:
                price = res.Items.Item.OfferSummary.LowestNewPrice.FormattedPrice
            except AttributeError:
                return get_attributes(list(get_random_item()[0][0:5]))
            item.append(price)
            execute_query("UPDATE items SET image=%s WHERE AIN=%s",
                      (str(image), item[2],))
            print item
            return item
    except psycopg2.IntegrityError:
        return ["error"]

def encode_xml(xml):
    if type(xml) is str:
        try:
            return str(xml.encode('utf-8'))
        except AttributeError and UnicodeDecodeError:
            return xml
    return xml

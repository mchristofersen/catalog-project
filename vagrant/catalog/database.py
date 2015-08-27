import psycopg2
import re


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


def get_random_items(int):

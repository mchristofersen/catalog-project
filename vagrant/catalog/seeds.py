from database import *
import psycopg2
import re
import json
from categories import categories

from amazonproduct import API
import amazonproduct
api = amazonproduct.API(cfg='./my-config-file', locale='us')

def s(str):
    return str.rstrip().lstrip()


for category in categories:
    if get_category_id(category):
        continue
    for item in api.item_search(category, Keywords='Sale', ItemPage='1'):
        id = item.ASIN
        parent = False
        nodes = api.item_lookup(str(id), ResponseGroup="BrowseNodes")
        b_node = nodes.Items.Item.BrowseNodes.BrowseNode.Ancestors.BrowseNode
        node_id, name = (b_node.BrowseNodeId, b_node.Name)
        result = api.browse_node_lookup(node_id)
        result = result.BrowseNodes.BrowseNode
        while not parent:
            try:
                result = result.Ancestors.BrowseNode
            except AttributeError:
                name = result.Name
                node_id = result.BrowseNodeId
                parent = True
        execute_query("""INSERT INTO categories VALUES (%s)""", (category,))
        result = api.browse_node_lookup(node_id)
        result = api.browse_node_lookup(
            result.BrowseNodes.BrowseNode.Children.BrowseNode.BrowseNodeId)
        for child in result.BrowseNodes.BrowseNode.Children.BrowseNode:
            try:
                execute_query("INSERT INTO subcategories VALUES (%s,%s)",
                              (str(child.Name), get_category_id(category),))
            except UnicodeEncodeError:
                continue
            i = 0
            for new_item in api.item_search(category,
                                            BrowseNode=str(
                                                child.BrowseNodeId)):
                subcat_id = execute_query("""
                    SELECT id FROM subcategories WHERE name=%s
                """,
                                          (child.Name.text,))[0][0]
                try:
                    item_id = new_item.ASIN.text
                    query = api.item_lookup(item_id,
                                            ResponseGroup='EditorialReview')
                    review = query.Items.Item.EditorialReviews.EditorialReview.Content.text
                    execute_query("""INSERT INTO items VALUES (%s,%s,%s,%s)
                                    """,
                                  (
                                      new_item.ItemAttributes.Title.text,
                                      review,
                                      item_id,
                                      subcat_id,
                                  )
                                  )
                except:
                    continue
                if i == 7:
                    break
                i += 1

        break

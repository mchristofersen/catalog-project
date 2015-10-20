from eb_catalog.database import *
from old.amazon_product_api import CREDENTIALS
import json
from flask.json import jsonify

api = amazonproduct.API(cfg=CREDENTIALS)

nodes = execute_query("""SELECT child_of, browse_node_name, browse_node_id, children_tree
                        FROM browse_nodes
                        WHERE depth = 1
                        ORDER BY child_of, browse_node_id
""")
n = None
for node in nodes[1:]:
    if node[0] != n:
        if n != None:
            query = execute_query("""UPDATE browse_nodes
                                    SET children_tree = %s
                                    WHERE browse_node_id = %s
            """, (json.dumps({"children":temp}),n,))
        n = node[0]
        if node[3] == None:
            temp= [[node[1],node[2]]]
        else:
            temp= [[node[1],node[2],node[3]]]
    else:
        if node[3] == None:
            temp.append([[node[1],node[2]]])
        else:
            temp.append([[node[1],node[2],node[3]]])
query = execute_query("""UPDATE browse_nodes
                                    SET children_tree = %s
                                    WHERE browse_node_id = %s
            """, (json.dumps({"children":temp}),n,))
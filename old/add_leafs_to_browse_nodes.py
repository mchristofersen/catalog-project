from eb_catalog.database import *

nodes = execute_query("SELECT id FROM leaf_nodes()")
nodes = [x[0] for x in nodes]

for node in nodes:
    execute_query("UPDATE browse_nodes SET leaf= 1 WHERE browse_node_id = %s",(node,))
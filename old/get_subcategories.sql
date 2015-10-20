DROP FUNCTION get_subcategories(text);
CREATE FUNCTION get_subcategories(text)
  RETURNS TABLE (name text, id text, leaf BOOLEAN) AS $$
    SELECT browse_node_name, browse_node_id,
    CASE WHEN leaf ISNULL THEN FALSE
         WHEN leaf = 1 THEN TRUE
    END
    FROM browse_nodes;
      $$LANGUAGE SQL;
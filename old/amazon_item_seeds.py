from lxml import objectify
from lxml import etree

from eb_catalog.database import *
from old.amazon_product_api import CREDENTIALS

objectify.enable_recursive_str()

def unescape(s):
    s = s.replace("&lt;", "<")
    s = s.replace("&gt;", ">")
    s = s.replace("&amp;", "&")
    s = s.replace('&quot;', '"')
    return s

api = amazonproduct.API(cfg=CREDENTIALS)

nodes = execute_query("SELECT * FROM item_counts(4)")
nodes.reverse()
for node in nodes:
    try:
        try:
            items = api.item_search(node[2], BrowseNode=node[0], ResponseGroup="ItemAttributes, Images, EditorialReview, OfferSummary", Sort='reviewrank')
        except amazonproduct.AWSError:
            items = api.item_search('Books', BrowseNode=node[0], ResponseGroup="ItemAttributes, Images, EditorialReview, OfferSummary", Sort='reviewrank')
        i = 0
        k = 0
        for page in items:
            for item in page[4:]:
                asin = item.ASIN
                images = list()
                try:
                    for x in item.iterchildren('{http://webservices.amazon.com/AWSECommerceService/2011-08-01}LargeImage'):
                        images.append(str(x.URL))
                    for x in item.ImageSets.iterchildren('{http://webservices.amazon.com/AWSECommerceService/2011-08-01}ImageSet'):
                        images.append(str(x.LargeImage.URL))
                except AttributeError:
                    print 'no pics'
                    continue
                except psycopg2.IntegrityError:
                    print 'nope'
                    continue
                name = item.ItemAttributes.Title
                try:
                    price = item.OfferSummary.LowestNewPrice.FormattedPrice
                except AttributeError:
                    try:
                        price = item.OfferSummary.ListPrice.FormattedPrice
                    except AttributeError:
                        # print etree.dump(item.Items.Item)
                        print 'price error'
                        continue
                ASIN = item
                try:
                    description = unescape(etree.tostring(item.EditorialReviews.EditorialReview.Content))
                except (UnicodeEncodeError,AttributeError):
                    try:
                        tree = item.ItemAttributes
                        iter = tree.iterchildren('{http://webservices.amazon.com/AWSECommerceService/2011-08-01}Feature')
                        string = '<ul>'
                        for element in iter:
                            string += '<li>'+str(element)+'</li>'
                        string += '</ul>'
                        description = string
                        print 'got features'
                    except (AttributeError, UnicodeEncodeError):
                        print 'review error'
                        continue
                try:
                    query = execute_query("INSERT INTO items (name, description, price, images, browse_node_id, asin) VALUES ( %s, %s, %s,%s,%s,%s)",
                                          (str(name),
                                           description,
                                           str(price),
                                           images,
                                           node[0],
                                           str(asin),))
                    # print list(str(name),
                    #                        description,
                    #                        str(price),
                    #                        images,
                    #                        node[0],
                    #                        str(asin),)
                except (UnicodeEncodeError, TypeError, psycopg2.IntegrityError):
                   continue
                if query and i < 5:
                    i +=1
                    print str(name)
                else:
                    break
            if i >4:
                print "next page"
                break
    except:
        print 'wtf'
        continue

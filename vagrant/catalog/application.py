from flask import Flask, render_template, request, redirect, url_for
from database import get_random_item, get_med_img, encode_xml, get_attributes
import operator
import sys
import time

application = Flask(__name__)
reload(sys)
sys.setdefaultencoding('utf8')
@application.route('/')
def home():
    then = time.time()
    item = list(get_random_item()[0][0:5])
    random = then-time.time()
    item = get_attributes(item)
    itime= then-time.time()
    item.append(random)
    item.append(itime)
    return render_template("home.html", item=[encode_xml(f) for f in item])

@application.route('/search')
def search(input='',category=''):
    return ''


if __name__ == '__main__':
    application.run(debug=True)

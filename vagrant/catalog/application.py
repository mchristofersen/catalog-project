from flask import Flask, render_template, request, redirect, url_for
from database import get_random_item, query_item
import json

app = Flask(__name__)


@app.route('/')
def home():
    item = get_random_item()[0]
    image = query_item(item[2])
    return render_template("home.html", item=item, image=image)


if __name__ == '__main__':
    app.run(debug=True, port=8000, host='192.168.33.10')

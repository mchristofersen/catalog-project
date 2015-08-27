import psycopg2
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route('/')
def home():
    return render_template("home.html")


if __name__ == '__main__':
    app.run(debug=True, port=8000, host='192.168.33.10')

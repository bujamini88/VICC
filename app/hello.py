from flask import Flask
import os

app = Flask(__name__)
conn = None

@app.route("/")
def hello():
    return "Flask inside Docker!!"


if __name__ == '__main__':
    app.run(host='0.0.0.0')

from flask import Flask, url_for

app = Flask(__name__)


@app.route("/")
def main_page():



if __name__ == "__main__":
    app.run(port=8080, host="127.0.0.1")
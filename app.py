from flask import Flask, url_for, render_template

app = Flask(__name__)


@app.route("/")
def main_page():
    return render_template('index.html')


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route("/profile")
def profile():
    return render_template('profile.html')


@app.route("/demo")
def demo():
    return render_template("demo.html")


if __name__ == "__main__":
    app.run(port=8080, host="127.0.0.1")
from flask import Flask, url_for, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from data import Product

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@app.route("/")
def main_page():
    products = db.session.execute(
        select(Product.id, Product.name, Product.price, Product.description, Product.image)
    ).all()
    return render_template('index1.html', products=products)


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route("/profile")
def profile():
    return render_template('profile.html')


@app.route("/demo/") #<int:index>
def demo():
    return render_template("demo.html")


if __name__ == "__main__":
    app.run(port=8080, host="127.0.0.1")
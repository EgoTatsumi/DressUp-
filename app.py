from flask import Flask, url_for, render_template

app = Flask(__name__)


@app.route("/")               #главная страница
def main_page():
    return render_template('index.html')

@app.route("/cart")           #корзина
def cart_page():
    return render_template('cart.html')

@app.route('/profile')
def profile_page():
    return render_template('profile.html')

@app.route('/demo')          #демонстрация товара
def demo_page():
    return render_template('demo.html')

@app.route('/sign_in')       #регистрация
def sign_in():
    return render_template('base.html')

if __name__ == "__main__":
    app.run(port=8080, host="127.0.0.1")
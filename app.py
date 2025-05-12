from flask import Flask, url_for, render_template, request, redirect, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from data import Product, User, db
import requests
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'u398hf@8euf98h23r9fuh23rh9fuh23rhf'
# import os
# app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key')

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

cart_list = {}

def get_products_with_quantity(product_dict):
    product_ids = list(product_dict.keys())

    products = Product.query.filter(Product.id.in_(product_ids)).all()

    result = []
    for product in products:
        result.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": round(product.price, 2),
            "image": product.image,
            "quantity": product_dict.get(product.id, 0)
        })

    return result


@app.route("/")
def main_page():
    products = Product.query.all()
    return render_template('index1.html', products=products)

@app.route("/add-to-cart", methods=["POST"])
def add_to_cart():
    data = request.get_json()
    print(f"Добавлено в корзину: {data}")
    # Здесь можно добавить товар в сессию или БД
    if cart_list.get(data['id']):
        cart_list[data['id']] += 1
    else:
        cart_list[data['id']] = 1
    print(cart_list)
    return jsonify({"success": True, "message": "Товар добавлен в корзину"})


@app.route('/cart')
def cart():
    return render_template('cart.html', cart_list=get_products_with_quantity(cart_list))


@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_user.name = request.form['full_name']
        current_user.city = request.form['city']
        current_user.address = request.form['address']
        current_user.email = request.form['email']
        current_user.phone = request.form['phone']
        db.session.commit()
        flash('Your information has been updated!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=current_user)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


with app.app_context():
    db.create_all()


# Регистрация
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Простая валидация email
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash("Неверный формат email.")
            return redirect(url_for('register'))

        if len(password) < 6:
            flash("Пароль должен содержать минимум 6 символов.")
            return redirect(url_for('register'))

        if User.query.filter_by(email=email).first():
            flash('Email уже используется.')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(name=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Успешная регистрация. Войдите в аккаунт.')
        return redirect(url_for('login'))

    return render_template('register.html')


# Вход
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash('Неверный email или пароль')
            return redirect(url_for('login'))

        login_user(user)
        return render_template('registration_success.html')
    return render_template('login.html')


@app.route('/plus-product/<int:id>', methods=['GET', 'POST'])
def plus(id):
    if request.method == 'POST':
        cart_list[id] += 1
    return render_template('cart.html', cart_list=get_products_with_quantity(cart_list), count=get_products_with_quantity(cart_list))


@app.route('/minus-product/<int:id>', methods=['GET', 'POST'])
def minus(id):
    if request.method == 'POST':
        if cart_list[id] > 1:
            cart_list[id] -= 1
    return render_template('cart.html', cart_list=get_products_with_quantity(cart_list))


# Выход
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# Приватная страница
@app.route('/dashboard')
@login_required
def dashboard():
    return f"Привет, {current_user.name}! Добро пожаловать в личный кабинет."


@app.route("/product_demo/<int:product_id>") #<int:index>
def product_demo(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_demo.html", product=product)


if __name__ == "__main__":
    app.run(port=8080, host="127.0.0.1")
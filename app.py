from flask import Flask, url_for, render_template, request, redirect, flash
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

@app.route("/")
def main_page():
    products = db.session.execute(
        select(Product.id, Product.name, Product.price, Product.description, Product.image)
    ).all()
    return render_template('index1.html', products=products)


@app.route('/cart')
def cart():
    return render_template('cart.html')


@app.route("/profile", methods=['GET', 'POST'])
def profile():
    user = User.query.first()

    if not user:
        flash('No user data found in database', 'error')
        return redirect(url_for('some_other_page'))

    if request.method == 'POST':
        user.name = request.form['full_name']
        user.city = request.form['city']
        user.address = request.form['address']
        user.email = request.form['email']
        user.phone = request.form['phone']

        db.session.commit()
        flash('Your information has been updated!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=user)

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
        return redirect(url_for('dashboard'))

    return render_template('login.html')

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
    return f"Привет, {current_user.username}! Добро пожаловать в личный кабинет."

@app.route("/demo/") #<int:index>
def demo():
    return render_template("demo.html")


if __name__ == "__main__":
    app.run(port=8080, host="127.0.0.1")
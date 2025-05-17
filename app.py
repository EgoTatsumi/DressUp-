from flask import Flask, url_for, render_template, request, redirect, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from data import Product, User, db, Order, OrderItem
import requests
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import re
from sqlalchemy.orm import joinedload

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


def get_products_with_quantity(cart_list):
    # Получаем все уникальные product_id из корзины
    product_ids = list({item['product_id'] for item in cart_list})

    # Загружаем соответствующие продукты из базы данных
    products = Product.query.filter(Product.id.in_(product_ids)).all()
    product_map = {product.id: product for product in products}

    result = []
    for item in cart_list:
        product = product_map.get(item['product_id'])
        if product:
            result.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": round(product.price, 2),
                "image": product.image,
                "quantity": item.get('quantity', 1),
                "size": item.get('size'),
                "color": item.get('color')
            })

    print("Cart input:", cart_list)
    print("Cart enriched:", result)
    return result



@login_manager.unauthorized_handler
def unauthorized_callback():
    # Если это AJAX-запрос, возвращаем JSON вместо редиректа
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': False, 'login_required': True}), 401
    else:
        return redirect(url_for('login'))


@app.route("/")
def main_page():
    products = Product.query.all()
    return render_template('index1.html', products=products)

@app.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    data = request.get_json()

    product_id = int(data.get('id'))  # обязательно приведение к int
    quantity = int(data.get('quantity'))
    size = data.get('size')
    color = data.get('color')
    price = float(data.get('price'))

    cart_item = {
        'product_id': product_id,
        'quantity': quantity,
        'size': size,
        'color': color,
        'price': price
    }

    cart = session.get('cart', [])

    # Проверка: если такой же товар уже есть — увеличиваем количество
    for item in cart:
        if item['product_id'] == product_id and item['size'] == size and item['color'] == color:
            item['quantity'] += quantity
            break
    else:
        cart.append(cart_item)

    session['cart'] = cart
    session.modified = True  # обязательно!
    return jsonify({'success': True, 'cart_count': len(cart)})



@app.route('/cart')
def cart():
    cart_items = session.get('cart', [])
    enriched_cart = get_products_with_quantity(cart_items)
    return render_template('cart.html', cart_list=enriched_cart)


@app.route('/orders')
@login_required
def orders():
    my_orders = (
        Order.query
        .filter_by(user_id=current_user.id)
        .options(
            joinedload(Order.items).joinedload(OrderItem.product)  # Загружаем позиции и товары
        )
        .order_by(Order.created_at.desc())
        .all()
    )
    return render_template('orders.html', orders=my_orders)

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


@app.route('/cart/plus/<int:id>', methods=["POST"])
def plus(id):
    cart = session.get('cart', [])
    for item in cart:
        if item['product_id'] == id:
            item['quantity'] += 1
            break
    session['cart'] = cart
    return redirect(url_for('cart'))


@app.route('/cart/minus/<int:id>', methods=["POST"])
def minus(id):
    cart = session.get('cart', [])
    for item in cart:
        if item['product_id'] == id and item['quantity'] > 1:
            item['quantity'] -= 1
            break
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart/remove', methods=["POST"])
def remove_item():
    product_id = int(request.form.get('product_id'))
    size = request.form.get('size', '').strip()
    color = request.form.get('color', '').strip()

    cart = session.get('cart', [])
    updated_cart = []

    for item in cart:
        if (item['product_id'] == product_id and
            item.get('size') == size and
            item.get('color', '').strip() == color):
            continue
        updated_cart.append(item)

    session['cart'] = updated_cart
    return redirect(url_for('cart'))





@app.route('/continue-shopping')
def continue_shopping():
    return redirect(url_for('main_page'))


@app.route('/checkout', methods=["POST"])
@login_required
def checkout():
    # Получаем ID текущего авторизованного пользователя
    user_id = current_user.id

    # Проверка корзины
    cart = session.get('cart', [])
    if not cart:
        return redirect(url_for('cart'))

    # Создаём заказ
    order = Order(user_id=user_id)
    db.session.add(order)
    db.session.commit()  # нужно сразу сохранить, чтобы появился order.id

    # Добавляем товары в заказ
    for item in cart:
        product = Product.query.get(item['product_id'])
        if not product:
            continue  # если товар не найден, пропускаем

        order_item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item['quantity'],
            size=item.get('size'),
            color=item.get('color', '').strip()
        )
        db.session.add(order_item)

    db.session.commit()
    session.pop('cart', None)  # очищаем корзину

    return redirect(url_for('orders'))  # лучше перенаправить на страницу заказов



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


@app.route("/product_demo/<int:product_id>")
def product_demo(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template("product_demo.html", product=product)


if __name__ == "__main__":
    app.run(port=8080, host="127.0.0.1")
from flask import Flask, redirect, request, render_template, url_for, flash, session

from database import Session, Users, MenuItem, Order, OrderItem, CartItem

from flask_caching import Cache

from flask_login import LoginManager, login_required, current_user, login_user, logout_user

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, Email
from flask_wtf.csrf import CSRFProtect

import logging

import os

import uuid

from datetime import datetime

app = Flask(__name__)

app.config["CACHE_TYPE"] = "simple"
app.config["CACHE_DEFAULT_TIMEOUT"] = 30
app.config["CACHE_KEY_PREFIX"] = "myapp_"

cache = Cache()
cache.init_app(app)

app.config["SECRET_KEY"] = "your_secret_key"
csrf = CSRFProtect(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    with Session() as session:
        user = session.query(Users).filter_by(id = user_id).first()
        if user:
            return user

@app.route("/")
@app.route("/home")
@login_required
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        nickname = request.form["nickname"]
        password = request.form["password"]

        with Session() as sess:
            user = sess.query(Users).filter_by(nickname=nickname).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for("home"))
            flash("Неправильне ім'я або пароль!", "danger")

    return render_template("login.html")

class RegisterForm(FlaskForm):
    nickname = StringField("Nickname", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":
        nickname = form.nickname.data
        email = form.email.data
        password = form.password.data

        with Session() as sess:
            existing_user = sess.query(Users).filter(
                (Users.nickname == nickname) | (Users.email == email)
            ).first()

            if existing_user:
                flash("Користувач із таким ім'ям або почтою вже існує!", "danger")
                return redirect(url_for("register"))
            
            new_user = Users(nickname=nickname, email=email)
            new_user.set_password(password)
            
            sess.add(new_user)
            sess.commit()
            
            login_user(new_user)
            return redirect(url_for("home"))
        
    return render_template("register.html", form=form)

class AddPositionForm(FlaskForm):
    name = StringField("Назва", validators=[DataRequired()])


@app.route("/add_position", methods=['GET', 'POST'])
@login_required
def add_position():
    if current_user.nickname != 'admin':
        return redirect(url_for('home'))

    form = AddPositionForm()
    
    if form.validate_on_submit():

        name = request.form['name']
        file = request.files.get('img')
        ingredients = request.form['ingredients']
        description = request.form['description']
        price = request.form['price']
        weight = request.form['weight']

        if not file or not file.filename:
            return 'Файл не вибрано або завантаження не вдалося'

        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        output_path = os.path.join('static/menu', unique_filename)

        with open(output_path, 'wb') as f:
            f.write(file.read())

        with Session() as cursor:
            new_position = MenuItem(name=name, ingredients=ingredients, description=description,
                                price=price, weight=weight, file_name=unique_filename)
            cursor.add(new_position)
            cursor.commit()

        flash('Позицію додано успішно!')

    return render_template('add_position.html', form=form)
        

@app.route('/menu')
@login_required
def menu():
    with Session() as session:
        all_positions = session.query(MenuItem).filter_by(active = True).all()
    return render_template('menu.html',all_positions = all_positions)

# функція для виходу
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# фунцкція для додавання товару у кошик
@app.route("/add_to_cart/<int:item_id>", methods=["POST", "GET"])
@login_required
def add_to_cart(item_id):
    with Session() as sess:
        existing = sess.query(CartItem).filter_by(user_id=current_user.id, item_id=item_id).first()
        if existing:
            existing.quantity += 1
        else:
            sess.add(CartItem(user_id=current_user.id, item_id=item_id))
        sess.commit()
    return redirect(url_for("menu"))


class CreateOrderForm(FlaskForm):
    submit = SubmitField("Оформити замовлення")
    
# функція для перегляду кошика
@app.route("/basket")
@login_required
def basket():
    basket_data = session.get('basket', {})
    form = CreateOrderForm()
    
    items = []
    total_price = 0
    with Session() as db:
        for name, qty in basket_data.items():
            item = db.query(MenuItem).filter_by(name=name).first()
            if item:
                total_price += item.price * int(qty)
                items.append({
                    'name': name,
                    'quantity': qty,
                    'price': item.price,
                    'total': item.price * int(qty)
                })
    
    return render_template('basket.html', items=items, total_price=total_price, form=form, basket=basket_data)


@app.route("/create_order", methods=["POST"])
@login_required
def create_order():
    form = CreateOrderForm()
    basket = session.get("basket", {})

    if not basket:
        flash("Кошик порожній", "danger")
        return redirect(url_for("menu"))

    with Session() as db:
        order = Order(
            user_id=current_user.id,
            order_time=datetime.now(),
            order_list=basket  # ✅ важливо! зберігаємо JSON
        )
        db.add(order)
        db.commit()  # order.id генерується тут

        # Додаємо позиції до order_items
        for name, qty in basket.items():
            item = db.query(MenuItem).filter_by(name=name).first()
            if item:
                order_item = OrderItem(
                    order_id=order.id,
                    item_id=item.id,
                    quantity=int(qty)
                )
                db.add(order_item)

        db.commit()
        session.pop("basket", None)
        flash("Замовлення створено успішно", "success")
        return redirect(url_for("my_orders"))


class AddToBasketForm(FlaskForm):
    name = StringField("Назва", validators=[DataRequired()])
    num = StringField("Кількість", validators=[DataRequired()])
    submit = SubmitField("Додати")

@app.route('/position/<name>', methods=['GET', 'POST'])
@login_required
def position(name):
    form = AddToBasketForm()
    
    with Session() as cursor:
        us_position = cursor.query(MenuItem).filter_by(active=True, name=name).first()

    if form.validate_on_submit():
        position_name = form.name.data
        position_num = form.num.data

        basket = session.get('basket', {})
        basket[position_name] = int(position_num)
        session['basket'] = basket

        flash("Позицію додано у кошик!")
        return redirect(url_for("menu"))

    return render_template('position.html', form=form, position=us_position)

# функція для праці з меню
@app.route('/manage_menu')
@login_required
def manage_menu():
    if current_user.nickname != 'admin':
        return redirect(url_for('home'))
    with Session() as session:
        all_positions = session.query(MenuItem).all()
    return render_template('manage_menu.html', positions=all_positions)

@app.route('/toggle_item/<int:item_id>')
@login_required
def toggle_item(item_id):
    if current_user.nickname != 'admin':
        return redirect(url_for('home'))
    with Session() as session:
        item = session.query(MenuItem).filter_by(id=item_id).first()
        if item:
            item.active = not item.active
            session.commit()
            flash(f"Стан позиції '{item.name}' змінено!", "info")
    return redirect(url_for('manage_menu'))


# функція для перегляду замовлень
@app.route("/my_orders")
@login_required
def my_orders():
    with Session() as db:
        orders = db.query(Order).filter_by(user_id=current_user.id).all()
        result = []
        for order in orders:
            items = []
            for oi in order.order_items:  # ✅ тут уже не буде конфлікту
                items.append({
                    "name": oi.item.name,
                    "quantity": oi.quantity
                })
            result.append({
                "id": order.id,
                "items": items,
                "time": order.order_time.strftime('%d.%m.%Y %H:%M')
            })
    return render_template("my_orders.html", orders=result)

@app.route("/our_shops")
@login_required
def our_shops():
    return render_template("our_shops.html")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)
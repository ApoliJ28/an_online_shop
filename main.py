from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import  DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Float
from config import SECRET_KEY, API_KEY_TEST
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from datetime import datetime
from form import RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from api_productos import APIProducts
import stripe

stripe.api_key = API_KEY_TEST

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
Bootstrap5(app)

# Configure Flask-Login

login_manager = LoginManager()
login_manager.init_app(app)


# Create database
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///online_shop.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# Create a User a table for all registered users.
class User(UserMixin, db.Model):
    __tablename__ = "user"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    mail: Mapped[str] = mapped_column(String(250), nullable=False)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    date_created: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
    last_login: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    cart_items = relationship("CartItems", back_populates="user_carts")
    pucharse = relationship("Pucharses", back_populates="user_pucharse")

class CartItems(db.Model):
    
    __tablename__ = 'cart_items'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('user.id'))
    id_product: Mapped[int] = mapped_column(Integer, nullable=False)
    name_product: Mapped[str] = mapped_column(String(300), nullable=False)
    description_product: Mapped[str] = mapped_column(String(300), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    price_product: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False, default='Processing')
    date_create: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
    date_update: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
    
    user_carts = relationship("User", back_populates="cart_items")

class Pucharses(db.Model):
    
    __tablename__ = 'purchases' 
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('user.id'))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    date_create: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now())
    
    user_pucharse = relationship("User", back_populates="pucharse")
    details = relationship("DetailsPucharses", back_populates="pucharse_details")

class DetailsPucharses(db.Model):
    
    __tablename__ = 'details_pucharses'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pucharse_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('purchases.id'))
    id_product: Mapped[int] = mapped_column(Integer, nullable=False)
    name_product: Mapped[str] = mapped_column(String(300), nullable=False)
    price_product: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    
    pucharse_details = relationship("Pucharses", back_populates="details")
    
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    products = APIProducts().get_limit_products()
    
    name = db.get_or_404(User, current_user.id).name if current_user.is_authenticated else None
    
    items_carts = db.session.execute(db.select(CartItems).where(CartItems.user_id == current_user.id, CartItems.status == 'Processing')).scalars().all() if current_user.is_authenticated else []
    
    total_cart = 0
    
    if items_carts:
        for item in items_carts:
            total_cart += item.total
    
    n_items = len(items_carts) if current_user.is_authenticated else 0
    
    return render_template('index.html', logged_in=current_user.is_authenticated, products=products, name=name, items_carts=items_carts, n_items=n_items, total_cart=round(total_cart,2))

@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    
    form=LoginForm()
    
    if form.validate_on_submit():
        user_login = db.session.execute(db.select(User).where(User.mail == form.mail.data)).scalar()
        if user_login is None:
            flash("That email does not exit. Please try again.")
            return redirect(url_for('login'))

        if check_password_hash(user_login.password, form.password.data):
            login_user(user_login)
            user_login.last_login = datetime.now()
            db.session.commit()
            return redirect(url_for('home'))
        else:
            flash('Password incorrect. Please try again.')
            return redirect(url_for('login'))
    
    return render_template('login.html', form=form, logged_in=current_user.is_authenticated)

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    
    form=RegisterForm()
    
    if form.validate_on_submit():
        user_mail = db.session.execute(db.select(User).where(User.mail == form.mail.data)).scalar()

        if user_mail is not None:
            flash("You've already singed ip with that email, log in instead!!")
            return redirect(url_for('register'))

        new_user = User(
            name=form.name.data,
            mail=form.mail.data,
            password=generate_password_hash(password=form.password.data, salt_length=8, method='pbkdf2:sha256'),
            last_login=datetime.now()
        )

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)

        return redirect(url_for('home'))
    
    return render_template('register.html', form=form, logged_in=current_user.is_authenticated)

@app.route('/auth/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/cart/add-item/<int:id_product>')
def add_item_cart(id_product):
    
    user_product = db.session.execute(db.select(CartItems).where(CartItems.id_product == id_product, CartItems.user_id == current_user.id, CartItems.status == 'Processing')).scalar()
    
    if user_product is None:
        product = APIProducts().get_product(id=id_product)
        if product:
            new_item_product = CartItems(
                user_id = current_user.id,
                img_url = product['image'],
                id_product = product['id'],
                name_product = product['title'],
                price_product = product['price'],
                description_product = product['description'],
                quantity = 1,
                total = product['price']
            )
        
            db.session.add(new_item_product)
            db.session.commit()
        else:
            flash('The product does not exist in the api.')
        
        return redirect(url_for('home'))
    
    flash('The product is already added to the cart')
    return redirect(url_for('home'))

@app.route('/cart/update_cart_item/<int:item_id>', methods=['POST'])
def update_cart_item(item_id):
    data = request.get_json()
    quantity = data.get('quantity')

    cart_item = CartItems.query.filter_by(id=item_id, user_id=current_user.id).first()
    if cart_item:
        cart_item.quantity = quantity
        cart_item.total = cart_item.price_product * quantity
        db.session.commit()
        return jsonify(success=True)
    
    return jsonify(success=False), 404

@app.route('/cart/delete_cart_item/<int:item_id>', methods=['DELETE'])
def delete_cart_item(item_id):
    cart_item = db.get_or_404(CartItems, item_id)
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        return jsonify(success=True)
    return jsonify(success=False), 404

@app.route('/pay/create-checkout-session', methods=['POST', 'GET'])
def create_checkout_session():
    items_carts = db.session.execute(db.select(CartItems).where(CartItems.user_id == current_user.id, CartItems.status == 'Processing')).scalars().all()

    line_items_pay = [
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": item.name_product,
                                            "images": [item.img_url]},
                        "unit_amount": int(item.price_product*100),
                    },
                    'quantity': item.quantity,
                    }
    for item in items_carts]

    checkout_session = stripe.checkout.Session.create(
        line_items=line_items_pay,
        mode='payment',
        success_url=f"http://127.0.0.1:5000/pay/success",
        cancel_url="http://127.0.0.1:5000/",
    )
    
    
    return redirect(checkout_session.url, code=303)

@app.route('/pay/success')
def pay_success():
    items_carts = db.session.execute(db.select(CartItems).where(CartItems.user_id == current_user.id, CartItems.status == 'Processing')).scalars().all()
    
    total_pay = 0
    total_quantity = 0
   
    for item in items_carts:
        total_pay += item.total
        total_quantity += item.quantity
        
        item.status = 'Completed'
        item.date_update = datetime.now()
    
    new_pucharse = Pucharses(
        user_id=current_user.id,
        quantity=total_quantity,
        total=total_pay
    )
    
    db.session.add(new_pucharse)
    db.session.commit()
    for item in items_carts:
        new_details_pucharse = DetailsPucharses(
            pucharse_id = new_pucharse.id,
            id_product = item.id_product,
            name_product = item.name_product,
            price_product = item.price_product,
            quantity= item.quantity,
            total = item.price_product * item.quantity
        )
        
        db.session.add(new_details_pucharse)
        db.session.commit()
    
    flash('Your purchase was completed successfully')
    
    return redirect(url_for('home'))
    
    

if __name__ == '__main__':
    app.run()
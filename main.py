from flask import Flask, render_template, flash, redirect, url_for
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import  DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, DateTime, Float
from config import SECRET_KEY
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from datetime import datetime
from form import RegisterForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
from api_productos import APIProducts

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
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    prince_product: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    satus: Mapped[str] = mapped_column(String(100), nullable=False, default='Processing')
    
    user_carts = relationship("User", back_populates="cart_items")

class Pucharses(db.Model):
    
    __tablename__ = 'purchases' 
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('user.id'))
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    voucher: Mapped[str] =  mapped_column(String(300), nullable=False)
    
    user_pucharse = relationship("User", back_populates="pucharse")
    details = relationship("DetailsPucharses", back_populates="pucharse_details")

class DetailsPucharses(db.Model):
    
    __tablename__ = 'details_pucharses'
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    pucharse_id: Mapped[int] = mapped_column(Integer, db.ForeignKey('purchases.id'))
    id_product: Mapped[int] = mapped_column(Integer, nullable=False)
    name_product: Mapped[str] = mapped_column(String(300), nullable=False)
    prince_product: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    
    pucharse_details = relationship("Pucharses", back_populates="details")
    
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    products = APIProducts().get_limit_products()
    
    return render_template('index.html', logged_in=current_user.is_authenticated, products=products)

@app.route('/login', methods=['GET', 'POST'])
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

@app.route('/register', methods=['GET', 'POST'])
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

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run()
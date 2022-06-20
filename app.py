from flask import Flask, redirect, render_template, request, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy, abort
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from wtforms.validators import DataRequired
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, current_user, login_user, logout_user, login_required 
import os

########################################
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['USER_ENABLE_EMAIL'] = False
db = SQLAlchemy(app)
categories = ["Sofas", "Tables", "Beds"]
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
login = LoginManager(app)
login.init_app(app)
login.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
    
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String, nullable=False)
    img = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    popularity = db.Column(db.Integer)
    isActive = db.Column(db.Boolean, default=True)
    
db.create_all()
db.session.commit()

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', form = form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/')
def index():
    items = Item.query.order_by(Item.popularity).all()
    return render_template('index.html', items = items)

@app.route('/catalog')
def catalog():
    items = Item.query.order_by(Item.price).all()
    return render_template('catalog.html', items = items, categories = categories)

@app.route('/product/<id>', methods=['POST', 'GET'])
def product(id):
    item = Item.query.get(id)
    return render_template('product.html', item=item)

@app.route('/cart', methods=['POST', 'GET'])
@login_required
def cart():
    if not session.get('cart'):
        session['cart'] = []
    return render_template('cart.html', cart=session['cart'])

@app.route('/cart/<int:product_id>', methods=['POST', 'GET'])
@login_required
def add_to_cart(product_id):
    if not session.get('cart'):
        session['cart'] = []
    session['cart'].append(product_id)
    return redirect(url_for('cart'))

@app.route('/delivery', methods=['POST', 'GET'])
def delivery():
    return render_template('delivery.html')

@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        title = request.form['title']
        category = request.form['category']
        img = request.form['img']
        price = request.form['price']
        popularity = request.form['popularity']
        
        item = Item(title=title, category=category, price=price, img=img, popularity=popularity)
        
        try:
            db.session.add(item)
            db.session.commit()
            return redirect("url_for('create')")
        except:
            return "Получилась ошибка"
    else:
        return render_template('create.html')

    
@app.route('/delete', methods=['POST', 'GET'])
def delete():
    if request.method == "POST":
        delete_id = request.form["delete_id"]
        itm = User.query.filter_by(id = delete_id).first()
        
        db.session.delete(itm)
        db.session.commit()
        return redirect(url_for('delete'))
    else:
        return render_template('delete.html')
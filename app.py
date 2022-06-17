from flask import Flask, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy, abort

########################################

def heapify(arr, n, i, condition):
    largest = i
    l = 2 * i + 1
    r = 2 * i + 2

    if l < n and int(arr[i][condition]) < int(arr[l][condition]):
        largest = l

    if r < n and int(arr[largest][condition]) < int( arr[r][condition]):
        largest = r

    if largest != i:
        arr[i],arr[largest] = arr[largest],arr[i]

        heapify(arr, n, largest, condition)

def heapSort(arr, condition):
    n = len(arr)

    for i in range(n, -1, -1):
        heapify(arr, n, i, condition)

    for i in range(n-1, 0, -1):
        arr[i], arr[0] = arr[0], arr[i]
        heapify(arr, i, 0, condition)

########################################
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String, nullable=False)
    img = db.Column(db.Text, nullable=False)
    title = db.Column(db.String(20), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    popularity = db.Column(db.Integer)
    isActive = db.Column(db.Boolean, default=True)

categories = ["Sofas", "Tables", "Beds"]

@app.route('/')
def index():
    items = Item.query.order_by(Item.popularity).all()
    return render_template('index.html', items = items)

@app.route('/catalog')
def catalog():
    items = Item.query.order_by(Item.price).all()
    return render_template('catalog.html', items = items, categories = categories)

@app.route('/profile', methods=['POST', 'GET'])
def profile():
    return render_template('profile.html')

@app.route('/<id>', methods=['POST', 'GET'])
def product(id):
    items = Item.query.order_by(Item.popularity).all()
    return render_template('product.html', items = items)

@app.route('/delivery', methods=['POST', 'GET'])
def delivery():
    return render_template('delivery.html')

@app.route('/cart', methods=['POST', 'GET'])
def cart():
    return render_template('cart.html')

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
            return redirect("/create")
        except:
            return "Получилась ошибка"
    else:
        return render_template('create.html')

    
@app.route('/delete', methods=['POST', 'GET'])
def delete():
    if request.method == "POST":
        delete_id = request.form["delete_id"]
        itm = Item.query.filter_by(id = delete_id).first()
        
        db.session.delete(itm)
        db.session.commit()
        return redirect("/delete")
    else:
        return render_template('delete.html')
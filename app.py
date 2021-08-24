import hmac
import sqlite3

from flask import Flask, request, jsonify, render_template
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS, cross_origin



class User(object):
    def __init__(self, id, username, password, client_email, phone_number, address):
        self.id = id
        self.username = username
        self.password = password
        self.client_email = client_email
        self.phone_number = phone_number
        self.address = address


# Creating register table


def init_user_table():
    conn = sqlite3.connect('reservation.db')
    print("Opened database successfully")

    conn.execute("CREATE TABLE IF NOT EXISTS clients(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "client_name TEXT NOT NULL,"
                 "client_surname TEXT NOT NULL,"
                 "client_username TEXT NOT NULL,"
                 "client_password TEXT NOT NULL, address TEXT NOT NULL, "
                 "phone_number INT NOT NULL,"
                 " client_email TEXT NOT NULL)")
    print("user table created")
    conn.close()


# Creating Login table


def init_post_table():
    with sqlite3.connect('reservation.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS login (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "client_username TEXT NOT NULL,"
                     "client_password TEXT NOT NULL,"
                     "login_date TEXT NOT NULL)")
    print("Login table created successfully.")


# Creating Products table


def init_product_table():
    with sqlite3.connect('reservation.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS product (id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "product_name TEXT NOT NULL,"
                     "price TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "images TEXT NOT NULL)")
    print("Product table created successfully.")


init_product_table()
init_user_table()
init_post_table()


def fetch_users():
    with sqlite3.connect('reservation.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients")
        users = cursor.fetchall()

        new_data = []

        for data in users:
            new_data.append(User(data[0], data[3], data[4], data[5], data[6], data[7]))
    return new_data


clients = fetch_users()

username_table = {u.username: u for u in clients}
userid_table = {u.id: u for u in clients}


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


app = Flask(__name__)
CORS(app)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

jwt = JWT(app, authenticate, identity)

@app.route('/protected')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/login/', methods=['GET', 'POST'])
def login():
    return render_template('/login.html')


@app.route('/client-registration/', methods=["POST"])
def user_registration():
    response = {}

    if request.method == "POST":
        first_name = request.form['client_name']
        last_name = request.form['client_name']
        username = request.form['client_username']
        password = request.form['client_password']
        address = request.form['address']
        phone_number = request.form['phone_number']
        client_email = request.form['client_email']

        with sqlite3.connect("reservation.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO clients("
                           "client_name,"
                           "client_surname,"
                           "client_username,"
                           "client_password,"
                           "address,phone_number,"
                           "client_email) VALUES(?, ?, ?, ?, ?, ?, ?)",
                           (first_name, last_name, username, password, address, phone_number, client_email))
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201

        return response


@app.route('/create-products/', methods=["POST"])
#@jwt_required()
def create_products():
    response = {}

    if request.method == "POST":
        product_name = request.form['product_name']
        price = request.form['price']
        description = request.form['description']
        images = request.form['images']

        with sqlite3.connect('reservation.db') as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO product("
                           "product_name,"
                           "price,"
                           "description, images) VALUES(?, ?, ?, ?)", (product_name, price, description, images))
            conn.commit()
            response["status_code"] = 201
            response['description'] = "Point_of_Sale products added successfully"
        return response

# Getting users


@app.route('/get-clients/', methods=["GET"])
def get_users():
    response = {}
    with sqlite3.connect("reservation.db") as conn:
        cursor = conn.cursor()
        cursor.row_factory = sqlite3.Row

        cursor.execute("SELECT * FROM clients")

        posts = cursor.fetchall()
        accumulator = []

        for i in posts:
            accumulator.append({k: i[k] for k in i.keys()})

    response['status_code'] = 200
    response['data'] = tuple(accumulator)
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)

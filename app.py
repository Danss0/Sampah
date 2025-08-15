from flask import Flask, flash, request, render_template, redirect, session, url_for, jsonify
from pymongo import MongoClient
from bson import ObjectId
from bson.objectid import ObjectId
import requests
import googlemaps
import math
import hashlib
from datetime import datetime
import os
import jwt
from datetime import datetime, timedelta
import io
from os.path import join, dirname
from dotenv import load_dotenv
from werkzeug.utils import secure_filename

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME =  os.environ.get("DB_NAME")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]

app = Flask(__name__, template_folder="templates", static_folder="static")

SECRET_KEY = 'secret0'
TOKEN_KEY = 'mytoken'
app.secret_key = os.urandom(24)

@app.route('/', methods=['GET'])
def index():
    token_receive = request.cookies.get(TOKEN_KEY)

    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )

        if "id" in payload:
            user_info = db.users.find_one({"email": payload["id"]})

            if user_info is not None:
                is_admin = user_info.get("category") == "admin"
                logged_in = True
                return render_template('templates_user/home.html', user_info=user_info, logged_in=logged_in, is_admin=is_admin)
            else:
                msg = 'User not found'
                return render_template('templates_user/home.html', msg=msg, logged_in=False)

        else:
            msg = 'Invalid token payload'
            return render_template('templates_user/home.html', msg=msg, logged_in=False)

    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem decoding the token'

    return render_template('templates_user/home.html', msg=msg, logged_in=False)



@app.route('/home_admin', methods = ['GET'])
def home_admin():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload =jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.admin.find_one({"email": payload["id"]})
        reports = list(db.reports.find())
        is_admin = user_info.get("category") == "admin"
        logged_in = True
        return render_template('templates_admin/home.html', user_info=user_info, reports=reports, logged_in = logged_in, is_admin = is_admin)
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('templates_admin/home.html', msg=msg)


@app.route('/signup')
def signup():
    return render_template('templates_user/register.html')


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/sign_up/save', methods=['POST'])
def sign_up():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    ktp_file = request.files.get('ktp')

    if db.users.find_one({'email': email}):
        return jsonify({'result': 'failed', 'message': 'Email sudah digunakan'})

    ktp_folder = os.path.join('static', 'ktp')
    os.makedirs(ktp_folder, exist_ok=True)

    if ktp_file and allowed_file(ktp_file.filename):
        extension = ktp_file.filename.rsplit('.', 1)[1].lower()
        filename = secure_filename(email + '_ktp.' + extension)
        filepath = os.path.join(ktp_folder, filename)
        ktp_file.save(filepath)

        relative_path = f"ktp/{filename}"
    else:
        return jsonify({'result': 'failed', 'message': 'File KTP tidak valid'})

    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    doc = {
        "name": name,
        "email": email,
        "category": 'visitor',
        "password": password_hash,
        "ktp_file": relative_path,
        "is_verified": False
    }

    db.users.insert_one(doc)
    return jsonify({'result': 'success'})


@app.route('/signin')
def signin():
    return render_template('templates_user/login.html')

@app.route('/sign_in', methods=['POST'])
def sign_in():
    email = request.form["email"]
    password = request.form["password"]
    print(email)
    pw_hash = hashlib.sha256(password.encode("utf-8")).hexdigest()
    print(pw_hash)
    result = db.users.find_one(
        {
            "email": email,
            "password": pw_hash,
        }
    )
    if result:
        payload = {
            "id": email,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find a user with that id/password combination",
            }
        )

@app.route('/signup/admin')
def admin_signup():
    return render_template('templates_admin/admin_register.html')

@app.route('/sign_up/admin', methods=['POST'])
def admin_sign_up():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()

    doc = {
        "name": name,
        "email": email,
        "category": 'admin', 
        "password": password_hash
    }

    db.admin.insert_one(doc)
    return jsonify({'result': 'success'})

@app.route('/signin/admin')
def admin_signin():
    return render_template('templates_admin/admin_login.html')

@app.route('/sign_in/admin', methods=['POST'])
def admin_sign_in():
    admin_email = request.form["email"]
    admin_password = request.form["password"]
    print(admin_email)
    admin_pw_hash = hashlib.sha256(admin_password.encode("utf-8")).hexdigest()
    print(admin_pw_hash)
    result = db.admin.find_one(
        {
            "email": admin_email,
            "password": admin_pw_hash,
            "category": "admin" 
        }
    )
    if result:
        payload = {
            "id": admin_email,
            "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

        return jsonify(
            {
                "result": "success",
                "token": token,
            }
        )
    else:
        return jsonify(
            {
                "result": "fail",
                "msg": "We could not find an admin with that id/password combination",
            }
        )

@app.route('/ktpfiles')
def ktpfiles():
    users = list(db.users.find({"category": "visitor"}))
    return render_template('templates_admin/ktpfiles.html', users=users)


@app.route('/verify_user/<user_id>', methods=['POST'])
def verify_user(user_id):
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"is_verified": True}})
    return redirect(url_for('ktpfiles'))


@app.route('/sign_out')
def sign_out():
    response = jsonify(message="Logged out!")
    response.set_cookie('mytoken', '', expires=0) 
    return response


@app.route('/logout', methods=['GET' ,'POST'])
def logout():
    session.clear() 
    return redirect('/')


@app.route('/about')
def about():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})
        if user_info:
            is_admin = user_info.get("category") == "admin"
            logged_in = True
        else:
            is_admin = False
            logged_in = False
        return render_template('templates_user/about.html', user_info=user_info, logged_in=logged_in, is_admin=is_admin)
    
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('templates_user/about.html', msg=msg)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(
            token_receive,
            SECRET_KEY,
            algorithms=['HS256']
        )
        user_info = db.users.find_one({"email": payload["id"]})

        if request.method == 'POST':
            nama = request.form.get('nama')
            email = request.form.get('email')
            pesan = request.form.get('pesan')

            db.contact.insert_one({
                'user_id': user_info['_id'],
                'nama': nama,
                'email': email,
                'pesan': pesan,
            })

        if user_info:
            is_admin = user_info.get("category") == "admin"
            logged_in = True
        else:
            is_admin = False
            logged_in = False

        return render_template('templates_user/contact.html', user_info=user_info, logged_in=logged_in, is_admin=is_admin)
    
    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('templates_user/contact.html', user_info=None, logged_in=False, is_admin=False, msg=msg)



UPLOAD_FOLDER = 'static/uploads'  
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/edit_report/<reports_id>', methods=['GET', 'POST'])
def edit_report(reports_id):
    reports = db.reports.find_one({'_id': ObjectId(reports_id)})

    if request.method == 'POST':
        update_data = {
            'nama': request.form.get('nama'),
            'address': request.form.get('address'),
            'pesan': request.form.get('pesan'),
        }

        if 'image' in request.files:
            image = request.files['image']
            if image.filename:
                image_path = f"images/{image.filename}"
                image.save(os.path.join(app.static_folder, image_path))
                update_data['image_path'] = image_path

        db.reports.update_one({'_id': ObjectId(reports_id)}, {'$set': update_data})
        return redirect(url_for('home_admin'))

    return render_template('templates_admin/edit.html', reports=reports)


@app.route('/delete_report/<reports_id>', methods=['POST'])
def delete_report(reports_id):
    db.reports.delete_one({'_id': ObjectId(reports_id)})
    return redirect(url_for('home_admin'))

@app.route('/delete_user/<user_id>', methods=['POST'])
def delete_user(user_id):
    user = db.users.find_one({"_id": ObjectId(user_id)})
    if user:
        if user.get("ktp_file"):
            file_path = os.path.join("static", user["ktp_file"])
            if os.path.exists(file_path):
                os.remove(file_path)

        db.users.delete_one({"_id": ObjectId(user_id)})
    
    return redirect(url_for('ktpfiles'))

@app.route('/detail', methods=['GET'])
def detail():
    token_receive = request.cookies.get(TOKEN_KEY)
    logged_in = False
    user_info = None

    if token_receive:
        try:
            payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
            if "id" in payload:
                user_info = db.users.find_one({"email": payload["id"]})
                if user_info:
                    logged_in = True
                return render_template('templates_user/detail.html', user_info=user_info, logged_in = logged_in)
        except jwt.ExpiredSignatureError:
             msg = 'Your token has expired'
        except jwt.exceptions.DecodeError:
             msg = 'There was a problem logging you in'

    if not logged_in:
        return redirect('/') 

    return render_template('templates_user/detail.html', user_info=user_info, msg=msg)


def get_coordinates_from_address(address):
    default_coords = (-6.950187, 107.583086)
    url = f"https://nominatim.openstreetmap.org/search?format=json&q={address}"
    
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data:
                location = data[0]
                return float(location['lat']), float(location['lon'])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching coordinates: {e}")
    return default_coords

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@app.route('/cek_pengaduan', methods=['GET', 'POST'])
def cek_pengaduan():
    token_receive = request.cookies.get(TOKEN_KEY)
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"email": payload["id"]})
        logged_in = True

        
        if request.method == 'POST':
            if not user_info.get('is_verified', False):
                flash("Akun Anda belum diverifikasi oleh admin.", "warning")
                return redirect(url_for('cek_pengaduan'))

            nama = request.form['nama']
            address = request.form['address']
            pesan = request.form['pesan']
            bukti_foto = request.files['bukti_foto']

            latitude, longitude = get_coordinates_from_address(address)
            filename = secure_filename(bukti_foto.filename)
            filepath = os.path.join('static', 'bukti', filename)
            bukti_foto.save(filepath)

            db.reports.insert_one({
                'user_id': user_info['_id'],
                'nama': nama,
                'address': address,
                'pesan': pesan,
                'latitude': latitude,
                'longitude': longitude,
                'bukti_foto': filename
            })
            return redirect(url_for('cek_pengaduan'))

        laporan_info = list(db.reports.find({'user_id': user_info['_id']}))
        rekomendasi_tempat_sampah = []

        latitude = 0.0
        longitude = 0.0

        tempat_sampah_list = [
            { "name": "TPS Kopo Cirangrang", "latitude": -6.961752, "longitude": 107.5816071 },
            { "name": "TPS Porib", "latitude": -6.9490000, "longitude": 107.5823889 },
            { "name": "TPS Babakan", "latitude": -6.9286125, "longitude": 107.5758243 },
        ]

        if laporan_info:
            try:
                latitude = float(laporan_info[0].get('latitude', 0.0))
                longitude = float(laporan_info[0].get('longitude', 0.0))
            except (TypeError, ValueError):
                latitude = 0.0
                longitude = 0.0


        for lokasi in tempat_sampah_list:
            distance = haversine(latitude, longitude, lokasi['latitude'], lokasi['longitude'])
            rekomendasi_tempat_sampah.append({
                'name': lokasi['name'],
                'latitude': lokasi['latitude'],
                'longitude': lokasi['longitude'],
                'distance': round(distance, 2)
            })

        rekomendasi_tempat_sampah.sort(key=lambda x: x['distance'])
        rekomendasi_tempat_sampah = rekomendasi_tempat_sampah[:3]

        return render_template(
            'templates_user/cek_pengaduan.html',
            user_info=user_info,
            logged_in=logged_in,
            laporan_info=laporan_info,
            rekomendasi_tempat_sampah=rekomendasi_tempat_sampah,
            user_lat=latitude,
            user_lon=longitude,
        )

    except jwt.ExpiredSignatureError:
        msg = 'Your token has expired'
    except jwt.exceptions.DecodeError:
        msg = 'There was a problem logging you in'
    return render_template('templates_user/cek_pengaduan.html', msg=msg)


@app.route('/cek_laporan', methods=['GET', 'POST'])
def cek_laporan():
    if request.method == 'POST':
        laporan_id = request.form['laporan_id']
        new_status = request.form['status_pengaduan']

        laporan = db.reports.find_one({'_id': ObjectId(laporan_id)})
        if laporan:
            result = db.reports.update_one(
                {'_id': ObjectId(laporan_id)},
                {'$set': {'status_pengaduan': new_status}}
            )
            if result.modified_count > 0:
                print(f"Status pengaduan {laporan_id} berhasil diperbarui.")
            else:
                print(f"Laporan {laporan_id} tidak terupdate.")

            user_id = laporan.get('user_id')
            if user_id:
                db.reports.update_many(
                    {'user_id': user_id},
                    {'$set': {'status_pengaduan': new_status}}
                )
        return redirect(url_for('home_admin'))

    laporan_info = db.reports.find()
    return render_template('templates_admin/cek_laporan.html', laporan_info=laporan_info)



if __name__ == '__main__':
    app.run(debug=True)
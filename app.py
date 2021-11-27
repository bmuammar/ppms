import qrcode
from pyzbar.pyzbar import decode
import cv2
import time
import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

UPLOAD_FOLDER = 'static/uploads/'
app.secret_key = "secret key"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
#db = SQL("sqlite:///final.db")
db = SQL(os.getenv("DATABASE_URL"))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash('Must Provide Username')
            return render_template("login.html")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash('Must Provide Password')
            return render_template("login.html")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash('Invalid Username and/or Password')
            return render_template("login.html")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/")
@login_required
def view():
    equipments = db.execute("SELECT equipment_name FROM equipment")
    return render_template("index.html", equipments = equipments)

@app.route("/view", methods=["GET", "POST"])
@login_required
def viewequip(): 
    if request.method == "POST":
        if 'file' not in request.files:
            flash("No File Part")
            return render_template("view.html")

        file = request.files['file']
        if file.filename == '':
            flash("Please Select Image")
            return render_template("view.html")
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            filepath = UPLOAD_FOLDER + file.filename

            if cv2.imread(filepath) is None:
                flash('NO QR Code In Photo')
                return render_template("view.html")

            equipmentqr = cv2.QRCodeDetector()
            val, point, straight_qrcode = equipmentqr.detectAndDecode(cv2.imread(filepath))

            if val == '':
                flash('NO QR Code In Photo')
                return render_template("view.html")

            rows = db.execute('SELECT equipment_name FROM equipment')
            if not any(d['equipment_name'] == val for d in rows):
                flash('Equipment Not Available in List')
                return render_template("view.html")

            history = db.execute("SELECT description, month, year, equipment_name FROM history JOIN equipment on history.equip_id = equipment.id WHERE equipment_name = ?",val)
            operation = db.execute("SELECT instruction, equipment_name FROM operation JOIN equipment on operation.equip_id = equipment.id WHERE equipment_name = ?", val)
            return render_template("view.html", history=history, operation=operation)

        else:
            flash('Allowed image types are - png, jpg, jpeg')
            return render_template("view.html")

    else:
        equipments = db.execute("SELECT equipment_name FROM equipment")
        return render_template("view.html", equipments = equipments)

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/login")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    positions = ["Mech Eng", "Elect Eng", "I&C Eng", "P&E Eng", "Operation Eng"]

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            flash('Missing Name')
            return render_template("register.html", positions = positions)

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash('Must Provide Password')
            return render_template("register.html", positions = positions)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            flash('Must Confirm Password')
            return render_template("register.html", positions = positions)

        elif not request.form.get("position"):
            flash('Must Select Position')
            return render_template("register.html", positions = positions)

        # search database for the same user
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # if there is a row means there is a user with same name
        if len(rows) != 0:
            flash('Username Already Registered')
            return render_template("register.html", positions = positions)

        # compare two passwords
        if request.form.get("password") != request.form.get("confirmation"):
            flash('Password Did not Match')
            return render_template("register.html", positions = positions)

        # save username and hashedpasswords in db
        username = request.form.get("username")
        position = request.form.get("position")
        hashpassword = generate_password_hash(request.form.get("password"))

        db.execute("INSERT INTO users (username, hash, position) VALUES(?, ?, ?)", username, hashpassword, position)

        # Redirect user to home page
        return redirect("/login")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html", positions = positions)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():

    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("equipmentname"):
            flash('Missing Equipment Name')
            return render_template("add.html")

        # Get equipment name from HTML form
        equipmentname = request.form.get("equipmentname")

        rows = db.execute("SELECT equipment_name FROM equipment")
        if any(d['equipment_name'] == equipmentname for d in rows):
            flash('Equipment Already in List')
            return render_template("add.html")

        # Make QRCode for the equipment name
        img = qrcode.make(equipmentname)

        # Save the image in the static folder
        img.save('static/uploads/' + equipmentname + '.jpg', 'JPEG')

        # Save the image name as a variable
        photo = 'static/uploads/' + equipmentname + '.jpg'

        # Convert the image to BLOB
        with open(photo, 'rb') as file:
            blobData = file.read()

        db.execute("INSERT INTO equipment (equipment_name, img_qrcode) VALUES(?, ?)", equipmentname, blobData)
        return redirect("/")
    else:
        return render_template("add.html")

@app.route("/history", methods=["GET", "POST"])
@login_required
def history():

    equipments = db.execute("SELECT equipment_name FROM equipment")

    if request.method == "POST":

        equipment = request.form.get("equipment")
        year = request.form.get("year")
        month = request.form.get("month")
        description = request.form.get("description")

        if not equipment or not year or not month or not description:
            flash('Missing Information')
            return render_template("history.html", equipments=equipments)

        equip_id = db.execute("SELECT id FROM equipment WHERE equipment_name = ?", equipment)
        equip_id = equip_id[0]['id']

        db.execute("INSERT INTO history(equip_id, month, year, description) VALUES(?, ?, ?, ?)", equip_id, month, year, description)

        history = db.execute("SELECT description, month, year, equipment_name FROM history JOIN equipment on history.equip_id = equipment.id WHERE equip_id = ?", equip_id)
        equipments = db.execute("SELECT equipment_name FROM equipment")
        return render_template("history.html", history = history, equipments = equipments)

    else:
        rows = db.execute('SELECT position FROM users WHERE id = ?', session['user_id'])
        allowed_employee = ['Mech Eng', 'Elect Eng', 'I&C Eng']
        if rows[0]['position'] not in allowed_employee:
            flash('You Are Not Authorized')
            return redirect('/')

        return render_template("history.html", equipments = equipments)

@app.route("/operation", methods=["GET", "POST"])
@login_required
def operation():
    equipments = db.execute("SELECT equipment_name FROM equipment")

    if request.method == "POST":
        # Ensure username was submitted

        equipment = request.form.get("equipment")
        instruction = request.form.get("instruction")

        if not equipment or not instruction:
            flash('Missing Information')
            return render_template("operation.html", equipments=equipments)

        equip_id = db.execute("SELECT id FROM equipment WHERE equipment_name = ?", equipment)
        equip_id = equip_id[0]['id']

        db.execute("INSERT INTO operation (equip_id, instruction) VALUES(?, ?)", equip_id, instruction)

        operation = db.execute(
            "SELECT instruction, equipment_name FROM operation JOIN equipment on operation.equip_id = equipment.id WHERE equip_id = ?",
            equip_id)
        equipments = db.execute("SELECT equipment_name FROM equipment")
        return render_template("operation.html", operation=operation, equipments=equipments)

    else:
        rows = db.execute('SELECT position FROM users WHERE id = ?', session['user_id'])
        allowed_employee = ['P&E Eng']
        if rows[0]['position'] not in allowed_employee:
            flash("You Are Not Authorized")
            return redirect('/')
        return render_template("operation.html", equipments=equipments)

@app.route("/cam", methods=["GET", "POST"])
@login_required
def cam():
    if request.method == "POST":
        video = cv2.VideoCapture(0)
        while True:
            check, frame = video.read()
            if frame is not None:
                time.sleep(3)
                for barcode in decode(frame):
                    if barcode.data.decode('utf-8') is not None:
                        val = barcode.data.decode('utf-8')
                        rows = db.execute('SELECT equipment_name FROM equipment')
                        if not any(d['equipment_name'] == val for d in rows):
                            flash('Equipment Not Available in List')
                            return render_template("view.html")
                        history = db.execute("SELECT description, month, year, equipment_name FROM history JOIN equipment on history.equip_id = equipment.id WHERE equipment_name = ?",val)
                        operation = db.execute("SELECT instruction, equipment_name FROM operation JOIN equipment on operation.equip_id = equipment.id WHERE equipment_name = ?",val)
                        return render_template("view.html", history=history, operation=operation)
            break
        flash('Try Again')
        return render_template("cam.html")
    else:
        return render_template("cam.html")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
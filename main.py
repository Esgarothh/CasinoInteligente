
import pyrebase
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for
import json
import firebase_admin
from firebase_admin import db
from firebase_admin import credentials
import re
import qrcode
import io
import base64
import serial

"""
ser = serial.Serial('/dev/ttyACM0',19200)

#with serial.Serial('/dev/ttyACM0', 57600,timeout=10) as ser:
opcion = ""
while True:
    linea = ser.readline()
    print(linea)


    matched = re.match("(^.*Send)|(^.*send)|(^.*Save)", linea.decode("utf-8") )
    is_match = bool(matched)
    #Load_cell output val
    #matched2 = re.match("(.*(Load_cell).*(output).*(val))", linea.decode("utf-8") )
    #match2 = bool(matched2)
    matched2 = re.match("(^.*Coloque)", linea.decode("utf-8") )
    match2 = bool(matched2)

    if is_match:
        opcion = input("valor:")
        ser.write(opcion.encode())
    if match2:
        opcion = input("valor:")
        ser.write(opcion.encode())
        break
"""

def leerPeso():
    while True:
        linea = ser.readline()
        matched2 = re.match("(.*(Load_cell).*(output).*(val))", linea.decode("utf-8") )
        match2 = bool(matched2)
        if match2:
            return linea

def led_compra(b):
    while True:
        #linea = ser.readline()
        #matched2 = re.match("(.*(leer).*(algo))", linea.decode("utf-8") )
        #match2 = bool(matched2)
        if b:
            while True:
                value = 'a'
                ser.write(value.encode())
                confir = ser.readline()
                print(confir)
                matched3 = re.match("(^.*confirmacion)", confir.decode("utf-8") )
                match3 = bool(matched3)
                if match3:
                    return 0
        if not b:
            while True:
                value = 'b'
                ser.write(value.encode())
                confir = ser.readline()
                matched3 = re.match("(^.*confirmacion)", confir.decode("utf-8") )
                match3 = bool(matched3)
                if match3:
                    break
            break


        #else:
        #    value = 'c'
        #    ser.write(value.encode())




    #linea = ser.readline()
    #print(linea)
    #opcion = input("valor:")
    #ser.write(opcion.encode())

    #if opcion == "t":
    #    ser.write(b't')
         
#s = ser.read(10)        # read up to ten bytes (timeout)
#       line = ser.readline()   # read a '\n' terminated line


databaseURL = "https://proyectotics-35614-default-rtdb.firebaseio.com"
cred_obj = firebase_admin.credentials.Certificate('proyectotics-35614-firebase-adminsdk-9742r-40c21ffde6.json')
default_app = firebase_admin.initialize_app(cred_obj, {
    'databaseURL':databaseURL
    })

ref = db.reference("/")





app = Flask(__name__)       #Initialze flask constructor
app.secret_key = "super secret key2"

#Add your own details
config = {
  "apiKey": "AIzaSyBP86fw6sn8IQrNRVuv9B7wEx8o5GhCArk",
  "authDomain": "proyectotics-35614.firebaseapp.com",
  "databaseURL": "https://proyectotics-35614-default-rtdb.firebaseio.com",
  "storageBucket": "proyectotics-35614.appspot.com"
}

#initialize firebase
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
dbase = firebase.database()

#global variables
error = ""


#Initialze person as dictionary
person = {"is_logged_in": False, "name": "", "email": "", "uid": "","estadoCompra":""}

#Login
@app.route("/")
def login():
    return render_template("login.html")

#Sign up/ Register
@app.route("/signup")
def signup():
    return render_template("signup.html", error = error)




@app.route("/testcomprar")
def testcomprar():
    led_compra(True)
    return render_template("espere_luz.html", error = error)

@app.route("/testsalir")
def testsalir():
    led_compra(False)
    return ""










@app.route("/signupError")
def signupError():
    error = request.args.get('error')
    flash(error)
    return render_template("signup.html", error = error)


def random_qr(url='www.google.com'):
    qr = qrcode.QRCode(version=1,
                       error_correction=qrcode.constants.ERROR_CORRECT_L,
                       box_size=10,
                       border=4)

    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image()
    return img



#Welcome page
@app.route("/welcome")
def welcome():
    if person["is_logged_in"] == True:

        img_buf = io.BytesIO()

        #linea = ser.readline()
        #print(linea)
                                        #ARDUINO


        #compra_ref = db.reference('usuarios')
        #url_user = db.order_by_child("email").get()
        #for i in url_user:
        #    print(i)

        img = random_qr(url=str(person['uid']))
        img.save(img_buf,"png")
        img_buf.seek(0)

        plot_url = base64.b64encode(img_buf.getvalue()).decode()

        formatted = 'data:image/png;base64,{}'.format(plot_url)
        return render_template("welcome.html", name=person["name"], email = person["email"], qrCode=formatted,compraText=person["estadoCompra"])
        #return render_template("camara.html", name=person["name"], email = person["email"])

    else:
        return redirect(url_for('login'))

#COmpratest page
@app.route("/comprar")
def comprar():
    print(person)
    if person["is_logged_in"] == True:
        dbase.child("users").child(person["uid"]).update({'compra':'true'})
        person["estadoCompra"] = defVal(person["uid"])
        return render_template("compraexitosa.html", email = person["email"], name = person["name"])
    else:
        return redirect(url_for('login'))




@app.route("/vender")
def vender():
    print(person)
    if person["is_logged_in"] == True:
        dbase.child("users").child(person["uid"]).update({'compra':'false'})
        return render_template("welcome.html", email = person["email"], name = person["name"])
    else:
        return redirect(url_for('login'))



#Purchase mode 
#@app.route("/validate", methods = ["POST","GET"])
def validate(uide):
    data = firebase.database()
    for cada in data.get().each():
        for llave in cada.val().keys():
            if uide == llave:
                jeison = json.dumps(cada.val()[llave])
                resp = json.loads(jeison)
                print("el usuario es:",jeison, "y compra es:", resp["compra"])
                if resp["compra"] == "false":
                    return False #render_template("compraFailure.html",nombre = resp["name"])
                dbase.child("users").child(llave).update({'compra':"false"})
                return True #render_template("compraexitosa.html", nombre = resp["name"] )


@app.route("/posDeCompra", methods = ["POST","GET"])
def posDeCompra():
    return render_template("cameraFront.html", name=person["name"], email = person["email"])
    #usuarios = data.child("users")


@app.route("/confirmarQr", methods = ["POST","GET"])
def confirmarQr():
    uid = request.args.get("uid")
    if validate(uid):
        #led_compra(True)
        return render_template("validacionExitosa.html", nombre = uid)
    return render_template("validacionFailure.html", nombre = uid)
    #usuarios = data.child("users"
    #for userid in usuarios.get().each():
    #    print(userid.val())
        #nombre = usuarios.child(userid).child("email").get()
        #print(nombre.val())

def defVal(uide):
    data = firebase.database()
    for cada in data.get().each():
        for llave in cada.val().keys():
            if uide == llave:
                jeison = json.dumps(cada.val()[llave])
                resp = json.loads(jeison)
                print("el usuario es:",jeison, "y compra es:", resp["compra"])
                if resp["compra"] == "false":
                    return "No tienes un almuerzo comprado actualmente!"
                return "Tienes una compra valida actualmente!" #render_template("compraexitosa.html", nombre = resp["name"] )

#If someone clicks on login, they are redirected to /result
@app.route("/result", methods = ["POST", "GET"])
def result():
    if request.method == "POST":        #Only if data has been posted
        result = request.form           #Get the data
        email = result["email"]
        password = result["pass"]
        try:
            #Try signing in the user with the given information
            user = auth.sign_in_with_email_and_password(email, password)
            #Insert the user data in the global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]

            person["estadoCompra"] = defVal(person["uid"])
            #Get the name of the user
            data = dbase.child("users").get()
            person["name"] = data.val()[person["uid"]]["name"]
            #Redirect to welcome page
            return redirect(url_for('welcome'))
        except Exception as e:
            print (e)
            #If there is any error, redirect back to login
            return redirect(url_for('login'))
    else:
        if person["is_logged_in"] == True:  
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('login'))



#If someone clicks on register, they are redirected to /register
@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":        #Only listen to POST
        result = request.form           #Get the data submitted
        email = result["email"]
        password = result["pass"]
        name = result["name"]
        try:
            #Try creating the user account using the provided data
            auth.create_user_with_email_and_password(email, password)
            #Login the user
            user = auth.sign_in_with_email_and_password(email, password)
            #Add data to global person
            global person
            person["is_logged_in"] = True
            person["email"] = user["email"]
            person["uid"] = user["localId"]
            person["name"] = name
            person["estadoCompra"] = "No tienes una compra activa"
            #Append data to the firebase realtime database
            data = {"name": name, "email": email,"compra":"false"}
            dbase.child("users").child(person["uid"]).set(data)
            #Go to welcome page

            """
            print("imhere") 
            ref = db.reference("/usuarios")
            usuario = {}  #diccionario vacio
            usuario["Nombre"] = name
            usuario["Correo"] = email
            json_usuario = json.dumps(usuario)
            for key, value in json_usuario.items():
                ref.push().set(value)
            """

            return redirect(url_for('welcome'))

        except Exception as e:
            
            if len(str(e))>0:
                error_as_string = (str(e).split(']',1))
                if len(error_as_string) > 1:
                    error_as_string = (error_as_string[1])
                    error_as_json = json.loads(error_as_string)
                    for key, value in error_as_json.items():
                        inside = value
                    error = inside.get('message')
                else:
                    error_as_string = (error_as_string[0])
                    error = error_as_string
                return redirect(url_for('signupError',error=error))
            else:


            

            #If there is any error, redirect to register
            #flash(error)
                return redirect(url_for('signupError',error=error))

    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome'))
        else:
            return redirect(url_for('register'))









if __name__ == "__main__":
    
    app.run(host='0.0.0.0')
    #app.run(ssl_context=('cert.pem', 'key.pem'))

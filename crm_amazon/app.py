from flask import Flask, render_template,request, redirect, session, flash
from pymongo import MongoClient
from datetime import datetime
from chatbot import responder
import json

app = Flask(__name__)
app.secret_key = "crm_secreto"

#MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["crm_amazon"]

clients = db["clientes"]
buys = db["compras"]
users = db["usuarios"]

#Create Admin
if users.count_documents({}) == 0:
    users.insert_one({
    "Usuario":"admin","password":"1234","rol":"admin"
})

#Login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = users.find_one({
            "Usuario": request.form["Usuario"],
            "password": request.form["password"]
        })

        if user:
            session["Usuario"] = user["Usuario"]
            return redirect("/dashboard")
        else:
            flash("Usuario o contraseña incorrectos")

    return render_template("login.html")
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

#Dashborad
@app.route("/dashboard")
def dashboard():
    if "Usuario" not in session:
        return redirect("/")
    total_clientes = clients.count_documents({})
    total_compras = buys.count_documents({})
    ingresos = sum([c.get["precio",0] for c in buys.find()])
    pipeline = [
        {"$group":{"_id":"$cliente_email","total":{"$sum":1}}},
        {"$sort":{"total":-1}}, {"$limit":1}
    ]
    frecuent = list(buys.aggregate(pipeline))
    frecuent_client = frecuent[0]["_id"] if frecuent else "N/A"
    return render_template(
        "dashboard.html",
        total_clientes=total_clientes,
        total_compras=total_compras,
        ingresos=ingresos,
        frecuent_client=frecuent_client
    )

#Clientes
@app.route("/clients",methods=["GET","POST"])
def clients_view():
    if "Usuario" not in session:
        return redirect("/")
    if request.method == "POST":
        clients.insert_one({
            "nombre":request.form["nombre"],
            "email":request.form["email"],
            "telefono":request.form["telefono"],
            "direccion":request.form["direccion"],
            "fecha":datetime.now().strftime("%Y-%m-%d")
        })
        return redirect("/clients")
    return render_template("clients.html",clients=clients.find())

#Compras
@app.route("/buys",methods=["GET","POST"])
def buy_view():
    if "Usuario" not in session:
        return redirect("/")
    if request.method == "POST":
        buys.insert_one({
            "cliente_email":request.form["email"],
            "producto":request.form["producto"],
            "precio":request.form["precio"],
            "fecha":datetime.now().strftime("%Y-%m-%d")
        })
        return redirect("/compras")
    return render_template("buys.html", buys=buys.find())

#Grafixa 
#@app.route("/grafica") 
#def grafica(): 
#    if "usuario" not in session: 
#        return redirect("/") 
#    pipeline = [{"$group": {"_id": "$cliente_email", "total": {"$sum": 1}}}] 
#    data = list(buys.aggregate(pipeline)) 
#    labels = [d["_id"] for d in data] 
#    values = [d["total"] for d in data] 
#    return render_template("grafica.html", labels=labels, values=values) 
@app.route("/grafica")
def grafica():
    if "Usuario" not in session:
        return redirect("/")

    pipeline = [{"$group": {"_id": "$cliente_email", "total": {"$sum": 1}}}]
    data = list(buys.aggregate(pipeline))

    labels = [d["_id"] for d in data]
    values = [d["total"] for d in data]

    return render_template(
        "grafica.html",
        labels=json.dumps(labels),
        values=json.dumps(values)
    )

#Chat
@app.route("/chat") 
def chat(): 
    if "Usuario" not in session: 
        return redirect("/") 
    return render_template("chat.html") 
@app.route("/chatbot", methods=["POST"]) 
def chatbot(): 
    mensaje = request.form["mensaje"] 
    respuesta = responder(mensaje) 
    return {"respuesta": respuesta} 

if __name__ == "__main__": 
    app.run(debug=True, use_reloader=False)
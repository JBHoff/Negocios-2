from flask import Flask, render_template, request, redirect, session, flash 
from pymongo import MongoClient 
from datetime import datetime 
app = Flask(__name__) 
app.secret_key = "crm_secreto" 
 
# MongoDB 
client = MongoClient("mongodb://localhost:27017/") 
db = client["crm_amazon_nochat"] 
 
clientes = db["clientes"] 
compras = db["compras"] 
usuarios = db["usuarios"] 
 
# Crear usuario admin si no existe 
if usuarios.count_documents({}) == 0: 
    usuarios.insert_one({ 
        "usuario": "admin", 
        "password": "1234", 
        "rol": "admin" 
    }) 
 
# ---------- LOGIN ---------- 
@app.route("/", methods=["GET", "POST"]) 
def login(): 
    if request.method == "POST": 
        user = usuarios.find_one({ 
            "usuario": request.form["usuario"], 
            "password": request.form["password"] 
        }) 
        if user: 
            session["usuario"] = user["usuario"] 
            return redirect("/dashboard") 
        else: 
            flash("Usuario o contraseña incorrectos") 
 
    return render_template("login.html") 
 
@app.route("/logout") 
def logout(): 
    session.clear() 
    return redirect("/") 
 
# ---------- DASHBOARD ---------- 
@app.route("/dashboard") 
def dashboard(): 
    if "usuario" not in session: 
        return redirect("/") 
 
    total_clientes = clientes.count_documents({}) 
    total_compras = compras.count_documents({}) 
 
    ingresos = sum([c["precio"] for c in compras.find()]) 
 
    pipeline = [ 
        {"$group": {"_id": "$cliente_email", "total": {"$sum": 1}}}, 
        {"$sort": {"total": -1}}, 
        {"$limit": 1} 
    ] 
    frecuente = list(compras.aggregate(pipeline)) 
    cliente_frecuente = frecuente[0]["_id"] if frecuente else "N/A" 
 
    return render_template( 
        "dashboard.html", 
        total_clientes=total_clientes, 
        total_compras=total_compras, 
        ingresos=ingresos, 
        cliente_frecuente=cliente_frecuente 
    ) 
 
# ---------- CLIENTES ---------- 
@app.route("/clientes", methods=["GET", "POST"]) 
def registrar_clientes(): 
    if "usuario" not in session: 
        return redirect("/") 
 
    if request.method == "POST": 
        clientes.insert_one({ 
            "nombre": request.form["nombre"], 
            "email": request.form["email"], 
            "telefono": request.form["telefono"], 
            "direccion": request.form["direccion"], 
            "fecha": datetime.now().strftime("%Y-%m-%d") 
        }) 
        return redirect("/clientes") 
 
    return render_template("clientes.html", clientes=clientes.find()) 
 
# ---------- COMPRAS ---------- 
@app.route("/compras", methods=["GET", "POST"]) 
def registrar_compras(): 
    if "usuario" not in session: 
        return redirect("/") 
 
    if request.method == "POST": 
        compras.insert_one({ 
            "cliente_email": request.form["email"], 
            "producto": request.form["producto"], 
            "precio": float(request.form["precio"]), 
            "fecha": datetime.now().strftime("%Y-%m-%d") 
        }) 
        return redirect("/compras") 
 
    return render_template("compras.html", compras=compras.find()) 
 
# ---------- GRÁFICA ---------- 
@app.route("/grafica") 
def grafica(): 
    if "usuario" not in session: 
        return redirect("/") 
 
    pipeline = [ 
        {"$group": {"_id": "$cliente_email", "total": {"$sum": 1}}} 
    ] 
    data = list(compras.aggregate(pipeline)) 
 
    labels = [d["_id"] for d in data] 
    values = [d["total"] for d in data] 
 
    return render_template("grafica.html", labels=labels, values=values) 
if __name__ == "__main__": 
    app.run(debug=True)
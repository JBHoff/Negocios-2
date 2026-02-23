from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["crm_amazon"]
compras = db["compras"]

def responder(mensaje):
    mensaje = mensaje.lower()

    if "ey" in mensaje:
        return "Ey folk, how can I help you?"
    if "compras" in mensaje:
        total = compras.count_documents({})
        return f"You have {total} registered buys."
    if "product" in mensaje or "ultima" in mensaje:
        ultima = compras.find().sort("fecha",-1).limit(1)
        for c in ultima:
            return f"Your las buy was {c['producto']} for ${c['precio']}"
    return "I didn't understand your message. Ask for buys or products."
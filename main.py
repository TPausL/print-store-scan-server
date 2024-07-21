from flask import Flask
from flask import request
import cv2 as cv
from image_processing import classify_color, analyze_color
from database import db, init_db
from models import Color, Product
from utils import *
import os
from dotenv import load_dotenv
from sqlalchemy import select, exc
from flask_json import FlaskJSON
import time

"""
    Setup the Flask app and the database connection.
"""
load_dotenv()
app = Flask(__name__)
json = FlaskJSON(app)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DSN")
db.init_app(app)
with app.app_context():
    init_db()


# New Product is added to the database
@app.route("/product", methods=["PUT", "POST"])
def store():
    
    if not request.data:
        return {"message": "Keine Bilddaten gesendet"}, 400
    nparr = np.fromstring(request.data, np.uint8)
    im = cv.imdecode(nparr, cv2.IMREAD_COLOR)
    cv.imwrite("./images/"+time.strftime("%Y%m%d-%H%M%S")+ ".jpeg",im) # Store image for later AI training

    colors = Color.query.all()
    thresholds = [(get_hsv_threshold(hex_to_hsv(c.hex))) for c in colors]

    # Until analysis is implemented, we use hardcoded default values
    shape = "6d8ef867-6123-43dd-a8a8-1650f9a3c772"
    size = "5d60af42-0789-4371-9e6a-aaa595f06edc"


    # find color of the product
    color_index = classify_color(im,thresholds)
    if color_index == -1:
        return {"message": "Farbe des Produktes wurde nicht gefunden"}, 404
    product = Product(shape_id=shape,size_id=size,color_id=colors[color_index].id)
    res_p: Product 

    # add one to existing product count or add new product
    try:
        try:
            existing_prod: Product = db.session.execute(
                select(Product)
                .where(Product.color_id == colors[color_index].id)
                .where(Product.shape_id == shape)
                .where(Product.size_id == size)
            ).scalar_one()
            res_p = existing_prod
            existing_prod.count = existing_prod.count + 1
        except Exception as e:
            res_p = product
            db.session.add(product)
        db.session.flush()
        db.session.commit()
        return {"message": "Ein Produkt wurde hinzugefügt", "data": {"color": res_p.color.text, "shape": res_p.shape.text, "size": res_p.size.text}}, 201

    except Exception as e:
        print(e)
        return {"message": "Fehler beim Hinzufügen des Produktes"}, 500


@app.route("/color", methods=["PUT", "POST"])
def post_color():
    if not request.data:
        return {"message": "Keine Bilddaten gesendet"}, 400
    nparr = np.fromstring(request.data, np.uint8)
    im = cv.imdecode(nparr, cv2.IMREAD_COLOR)
    #find color of the product and save as new color in database
    hex_str = analyze_color(im)
    text = "unbenannte Farbe"
    color = Color(hex=hex_str,text=text,display_hex=hex_str)
    try:
        db.session.add(color)
        db.session.commit()
    except exc.IntegrityError as e:
        return {"message": "Farbe bereits vorhanden", "data": {"text": color.text, "hex": color.hex}}, 200 #304 cant send additional data
    except Exception as e:
        return {"message": "Fehler beim Hinzufügen der Farbe"}, 500
    return {"message": "added one color", "data": {"text": color.text, "hex": color.hex}}, 201






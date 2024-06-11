from flask import Flask
from flask import request
import cv2 as cv
from image_processing import classify_color, analyze_color
from database import db, init_db
from models import Color, Product
from utils import *
import os
from dotenv import load_dotenv
from sqlalchemy import select

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DSN")
db.init_app(app)

with app.app_context():
    init_db()

@app.route("/product", methods=["PUT"])
def store():
    colors = Color.query.all()
    #names = [c.text for c in colors]
    thresholds = [(get_hsv_threshold(hex_to_hsv(c.hex))) for c in colors]
    f = request.files["image"]
    f.save("im")
    im = cv.imread("im")

    shape = request.form["shape"]
    size = request.form["size"]
    color_index = classify_color(im,thresholds)
    if color_index == -1:
        return "could not find color in database, you may add a new color with the /color request!", 404
    product = Product(shape_id=shape,size_id=size,color_id=colors[color_index].id)
    product
    try:
        existing_prod: Product = db.session.execute(
            select(Product)
            .where(Product.color_id == colors[color_index].id)
            .where(Product.shape_id == shape)
            .where(Product.size_id == size)
        ).scalar_one()
        existing_prod.count = existing_prod.count + 1
        db.session.flush()
    except Exception as e:
        db.session.add(product)
    db.session.commit()


    return "Succesfully added one product with color " + colors[color_index].text + " to database"

@app.route("/color", methods=["PUT"])
def post_color():
    f = request.files["image"]
    f.save("im")
    im = cv.imread("im")
    hex_str = analyze_color(im)
    text = request.form["text"]
    color = Color(hex=hex_str,text=text)
    db.session.add(color)
    db.session.commit()
    return "success fully added "+ text + " with color " + hex_str






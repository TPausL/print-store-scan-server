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
from flask_json import FlaskJSON, json_response
import time
load_dotenv()

app = Flask(__name__)

json = FlaskJSON(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DSN")
db.init_app(app)

with app.app_context():
    init_db()

@app.route("/product", methods=["PUT", "POST"])
def store():
    colors = Color.query.all()
    #names = [c.text for c in colors]
    thresholds = [(get_hsv_threshold(hex_to_hsv(c.hex))) for c in colors]
    nparr = np.fromstring(request.data, np.uint8)
    # decode image
    im = cv.imdecode(nparr, cv2.IMREAD_COLOR)
    cv.imwrite("./images/"+time.strftime("%Y%m%d-%H%M%S")+ ".jpeg",im)

    shape = "6d8ef867-6123-43dd-a8a8-1650f9a3c772"
    size = "5d60af42-0789-4371-9e6a-aaa595f06edc"
    color_index = classify_color(im,thresholds)
    if color_index == -1:
        return {"message": "Not found", "data": {"bla": "cool"}}, 404
    product = Product(shape_id=shape,size_id=size,color_id=colors[color_index].id)
    res_p: Product 
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
    return {"message": "added one object", "data": {"color": res_p.color.text, "shape": res_p.shape.text, "size": res_p.size.text}}, 201


@app.route("/test", methods=["GET"])
def test():
    return "hello", 200
@app.route("/color", methods=["PUT"])
def post_color():
    f = request.files["image"]
   
    f.save("im.jpeg")
    im = cv.imread("im.jpeg")
    hex_str = analyze_color(im)
    text = request.form["text"]
    color = Color(hex=hex_str,text=text)
    db.session.add(color)
    db.session.commit()
    return {"message": "added one color", "data": {"text": color.text, "hex": color.hex}}, 201






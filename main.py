from flask import Flask
from flask import request
import cv2 as cv
from image_processing import classify_color, analyze_color, get_size
from database import db, init_db
from models import Color, Product, Size
from utils import *
import os
from dotenv import load_dotenv
from sqlalchemy import select
from flask_json import FlaskJSON, json_response
import time
import sqlalchemy.exc as exc
from flask_sse import sse
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)



app.config["REDIS_URL"] = os.getenv("REDIS_URL")
app.register_blueprint(sse, url_prefix='/stream')


json = FlaskJSON(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DSN")
db.init_app(app)

with app.app_context():
    init_db()

@app.route("/product", methods=["PUT", "POST"])
def store():
   
    if not request.data:
        return {"message": "Keine Bilddaten gesendet"}, 400
    nparr = np.fromstring(request.data, np.uint8)
    # decode image
    try:
        im = cv.imdecode(nparr, cv2.IMREAD_COLOR)
    except Exception as e:
        return {"message": "Fehler beim Lesen des Bildes"}, 400
    cv.imwrite("./images/"+time.strftime("%Y%m%d-%H%M%S")+ ".jpeg",im)


    colors = Color.query.all()
    thresholds = [(get_hsv_threshold(hex_to_hsv(c.hex))) for c in colors]
    color_index = classify_color(im,thresholds)
    if color_index == -1:
        print("Color not found")
        return {"message": "Die Farbe wurde nicht gefunden"}, 404
    

    sizes = Size.query.all()
    size = get_size(im)
    possible_sizes = []
    for s in sizes:
        rel_diff = abs( (s.width - size[0]) / size[0])
        print(s.text + " " + str(rel_diff))
        if(rel_diff < 0.3):
            possible_sizes.append((s,rel_diff))
    
    if len(possible_sizes) == 0:
        return {"message": "Die Größe wurde nicht gefunden"}, 404
    possible_sizes = sorted(possible_sizes, key=lambda x: x[1])

    size = possible_sizes[0]
    
    shape = "6d8ef867-6123-43dd-a8a8-1650f9a3c772" # hardcoded shape until we have a shape detection
    size_id = size[0].id
    
    product = Product(shape_id=shape,size_id=size_id,color_id=colors[color_index].id)
    res_p: Product 
    try:
        existing_prod: Product = db.session.execute(
            select(Product)
            .where(Product.color_id == colors[color_index].id)
            .where(Product.shape_id == shape)
            .where(Product.size_id == size_id)
        ).scalar_one()
        res_p = existing_prod
        existing_prod.count = existing_prod.count + 1
    except Exception as e:
        res_p = product
        db.session.add(product)
    db.session.flush()
    db.session.commit()
    sse.publish({"message": "added one object", "data": {"color": res_p.color.text, "shape": res_p.shape.text, "size": res_p.size.text}},type="new_product")
    return {"message": "added one object", "data": {"color": res_p.color.text, "shape": res_p.shape.text, "size": res_p.size.text}}, 201


@app.route("/test", methods=["GET"])
def test():
    return "hello", 200
@app.route("/color", methods=["PUT"])
def post_color():
    if not request.data:
        return {"message": "Keine Bilddaten gesendet"}, 400
    nparr = np.fromstring(request.data, np.uint8)
    im = cv.imdecode(nparr, cv2.IMREAD_COLOR)
    #find color of the product and save as new color in database
    hex_str = analyze_color(im)
    text = "-- unbenannte Farbe --"
    color = Color(hex=hex_str,text=text,display_hex=hex_str)
    try:
        db.session.add(color)
        db.session.commit()
    except exc.IntegrityError as e:
        sse.publish({"message": "Farbe bereits vorhanden", "data": {"text": color.text, "hex": color.hex}},type="new_color_exists")
        return {"message": "Farbe bereits vorhanden", "data": {"text": color.text, "hex": color.hex}}, 200 #304 cant send additional data
    except Exception as e:
        return {"message": "Fehler beim Hinzufügen der Farbe"}, 500
               
    sse.publish({"message": "added one color", "data": {"text": color.text, "hex": color.hex}},type="new_color")
    return {"message": "added one color", "data": {"text": color.text, "hex": color.hex}}, 201






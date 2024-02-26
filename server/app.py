import hashlib
from flask import request, Response, Flask, jsonify, session, send_from_directory
from flask_cors import CORS, cross_origin
from ultralytics import YOLO
from PIL import Image
from werkzeug.utils import secure_filename
import cvzone
import cv2
import json
import os
import nest_asyncio
from geopy.geocoders import Nominatim
from modules.detect_object_on_video import detect_object_on_video
from flask_sqlalchemy import SQLAlchemy
from blueprints.auth.auth import auth_bp
import uuid

# AUTH AND MONGODB
from bson import ObjectId
from pymongo import MongoClient
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity, jwt_required
import datetime

client = MongoClient("localhost", 27017)
mongo_db = client.flask_database

# CLOUDINARY
import cloudinary
import cloudinary.api
import os
from dotenv import load_dotenv
load_dotenv()

# db=SQLAlchemy()
app = Flask(__name__, static_folder='static')
# app.config['SECRET_KEY'] = 'ebrajdon'
app.config['UPLOAD_FOLDER'] = 'static/videos'
# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"

# JWT... 
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY']='ebrajdon'
app.config['JWT_ACCESS_TOKEN_EXPIRES']=datetime.timedelta(days=1)
app.register_blueprint(auth_bp)

# db.init_app(app)
accidents_collection = mongo_db.accidents
users_collection = mongo_db.users
CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

# Creating the model
# class Accident(db.Model):
#     id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
#     address = db.Column(db.String(100), nullable=False)
#     city = db.Column(db.String(100), nullable=False)
#     latitude = db.Column(db.String(100), nullable=False)
#     longitude = db.Column(db.String(100), nullable=False)
#     severtyInPercentage = db.Column(db.Integer, nullable=False)
#     severty = db.Column(db.String(100), nullable=False)
#     def __repr__(self):
#         return f"User('{self.username}', '{self.email}')"

# GENERATE FRAMES
def generate_frames(path_x = ''):
    yolo_output = detect_object_on_video(path_x)
    for detection_ in yolo_output:
        ref,buffer=cv2.imencode('.jpg',detection_)

        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')
@app.route('/api/home',methods=['GET'])
def return_home():
    return jsonify({
        "message": "Welcome to home api page."
    })

@app.route('/api/apply-model', methods=['POST'])
def detect_object():
    try:
        image_file = request.files['image']
        boxes = detect_object_on_image(Image.open(image_file.stream))
        return Response(
            json.dumps(boxes),
            mimetype='application/json'
        )
    except Exception as e:
        return jsonify({
            "status": 'error',
            'message': str(e)
        })
    
def detect_object_on_image(image_file):
    # model = YOLO('./models/yolov8n.pt')
    model = YOLO('./models/current.pt')
    results = model.predict(image_file)
    result = results[0]
    output = []
    for box in result.boxes:
        x1,y1,x2,y2 = [
            round(x) for x in box.xyxy[0].tolist()
        ]
        class_id = box.cls[0].item()
        prob = round(box.conf[0].item(),2)
        output.append([
            x1,y1,x2,y2,result.names[class_id],prob
        ])
    return output

@app.route('/api/upload-video', methods=['POST'])
def api_video():
    print('🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥')
    print(request.method)
    video_file = request.files['image']
    video_file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(video_file.filename)))
    # video_path = os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(video_file.filename))
    video_path = video_file.filename
    if request.method == 'POST':
        # session['video_path'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],secure_filename(video_file.filename))
        # session['video_path'] = 'static/videos/bikes.mp4'
        return Response(
            json.dumps({
                "status": "success",
                "path": video_path
            }),
        )
        # return Response(generate_frames(path_x='static/videos/Accident-1.mp4'), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/show-video/static/videos/<path>', methods=['GET'])
def show_video(path):
    print('🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥')
    final_path = 'static/videos/' + path
    return Response(generate_frames(path_x=final_path), mimetype='multipart/x-mixed-replace; boundary=frame')  
    
@app.route('/api/webcam', methods=['GET'])
def api_webcam():
    return Response(generate_frames(path_x=0), mimetype='multipart/x-mixed-replace; boundary=frame')


# ROUTE TO POST ACCIDENT
@app.route('/api/v1/accident', methods=['POST'])
def api_accident():
    if request.method == 'POST':
        accident_data = request.get_json()
        accidents_collection.insert_one({
            address : accident_data["address"],
            city : accident_data['city'],
            latitude : accident_data['latitude'],
            longitude : accident_data['longitude'],
            severtyInPercentage : accident_data['severtyInPercentage'],
            severty : accident_data['severty']      
        })
        return jsonify({
            "status": "success",
            "message": "Accident data saved successfully."
        }), 201
    else:
        return jsonify({
            "status": 'failure'
        }), 404
        # accident = Accident(
        #     address=data["address"],
        #     city=data['city'],
        #     latitude=data['latitude'],
        #     longitude=data['longitude'],
        #     severtyInPercentage=data['severtyInPercentage'],
        #     severty=data['severty']
        # )
        # db.session.add(accident)
        # db.session.commit()
    
# ROUTE FOR GETTING ALL ACCIDENT DATA
@app.route("/api/v1/accident", methods=['GET'])
def api_accident_datas():
    allDatas = Accident.query.all()
    return jsonify({
        "status": "success",
        "datas": [
            {
                "id": data.id,
                "address": data.address,
                "city": data.city,
                "latitude": data.latitude,
                "longitude": data.longitude,
                "severtyInPercentage": data.severtyInPercentage,
                "severty": data.severty
            } for data in allDatas
        ]
    })
    
# ROUTE TO GET INDIVIDUAL ACCIDENT
@app.route("/api/v1/accident/<accidentId>", methods=["GET"])
def get_single_accident(accidentId):
    accident = Accident.query.filter_by(id=accidentId).first()
    return jsonify({
        "status": "success",
        "data": {
            "id": accident.id,
            "address": accident.address,
            "city": accident.city,
            "latitude": accident.latitude,
            "longitude": accident.longitude,
            "severtyInPercentage": accident.severtyInPercentage,
            "severty": accident.severty
        }
    })
    
# ROUTE TO GET THE GEO
# @app.route('/api/v1/get-geo',methods=['GET'])
# def api_getgeo():
#     location = Nominatim(user_agent="server")
#     getLoc = location.reverse("28.237987,83.995588")
#     return jsonify({
#         "status": "success",
#         "location": {
#             "address": getLoc.address,
#             "latitude": getLoc.latitude,
#             "longitude": getLoc.longitude,
#             "city": getLoc.raw.get("address", {}).get("city"),
#         }
#     })

if __name__ == '__main__':
    app.run(debug=True, port=8080)
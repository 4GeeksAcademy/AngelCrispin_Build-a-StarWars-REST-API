"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Favorites, Vehicle, Planet, Character
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)


# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route("/people", methods=["GET"])
def get_people():
    try:
        characters_db = Character.query.all()
        get_all_characters = list(
            map(lambda personage: personage.serialize(), characters_db)
        )
        return jsonify(get_all_characters), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/people/<int:people_id>", methods=["GET"])
def get_personage(people_id):
    try:
        character_db = Character.query.filter_by(id=people_id).first()
        if not character_db:
            return jsonify({"error": "Character not found"}), 404
        return jsonify(character_db.serialize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/planets", methods=["GET"])
def get_planets():
    try:
        planets_db = Planet.query.all()
        get_all_planets = list(map(lambda planet: planet.serialize(), planets_db))
        return jsonify(get_all_planets), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/planet/<int:planet_id>", methods=["GET"])
def get_planet(planet_id):
    try:
        planet_db = Planet.query.filter_by(id=planet_id).first()
        if not planet_db:
            return jsonify({"error": "Planet not found"}), 404
        return jsonify(planet_db.serialize()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users", methods=["GET"])
def get_users():
    try:
        users_db = User.query.all()
        show_users = list(map(lambda user: user.serialize(), users_db))
        return jsonify(show_users), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/<int:user_id>/favorites", methods=["GET"])
def get_user_favorites(user_id):
    try:
        user_db = User.query.filter_by(id=user_id).first()
        if not user_db:
            return jsonify({"error": "User not found"}), 404

        character_id_favorites = Favorites.query.filter_by(user_id=user_id, type=1)
        planet_id_favorites = Favorites.query.filter_by(user_id=user_id, type=2)
        vehicle_id_favorites = Favorites.query.filter_by(user_id=user_id, type=3)

        characters=[]
        planets=[]
        vehicles=[]

        for character_favorite in character_id_favorites:
            character = Character.query.filter_by(id=character_favorite.type_id).first()
            if character:
                characters.append(character.serialize())

        for planet_favorite in planet_id_favorites:
            planet = Planet.query.filter_by(id=planet_favorite.type_id).first()
            if planet:
                planets.append(planet.serialize())

        for vehicle_favorite in vehicle_id_favorites:
            vehicle = Vehicle.query.filter_by(id=vehicle_favorite.type_id).first()
            if vehicle:
                vehicles.append(vehicle.serialize())

        response = {
            "user": user_db.serialize(),
            "planets": planets,
            "vehicles": vehicles,
            "characters": characters,
        }

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/users/favorites", methods=["POST"])
def post_user_favorites():
    try:

        data = request.get_json()
        user_id=data["user_id"]
        user_db = User.query.filter_by(id=user_id).first()
        if not user_db:
            return jsonify({"error": "User not found"}), 404

        character_id_favorites = Favorites.query.filter_by(user_id=user_id, type=1)
        planet_id_favorites = Favorites.query.filter_by(user_id=user_id, type=2)
        vehicle_id_favorites = Favorites.query.filter_by(user_id=user_id, type=3)

        characters=[]
        planets=[]
        vehicles=[]

        for character_favorite in character_id_favorites:
            character = Character.query.filter_by(id=character_favorite.type_id).first()
            if character:
                characters.append(character.serialize())

        for planet_favorite in planet_id_favorites:
            planet = Planet.query.filter_by(id=planet_favorite.type_id).first()
            if planet:
                planets.append(planet.serialize())

        for vehicle_favorite in vehicle_id_favorites:
            vehicle = Vehicle.query.filter_by(id=vehicle_favorite.type_id).first()
            if vehicle:
                vehicles.append(vehicle.serialize())

        response = {
            "user": user_db.serialize(),
            "planets": planets,
            "vehicles": vehicles,
            "characters": characters,
        }

        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/favorite/planet/<int:planet_id>", methods=["POST"])
def add_planet_to_favorites(planet_id):
    try:

        data = request.get_json()
        user_id=data["user_id"]
        user_db = User.query.filter_by(id=user_id).first()
        if not user_db:
            return jsonify({"error": "User not found"}), 404
    
        if Favorites.query.filter_by(user_id=user_id, type_id=planet_id,type=2).first():
            return jsonify({"error": "Planet already added to favorites"}), 400

        db.session.add(Favorites(user_id=user_id, type_id=planet_id,type=2))
        db.session.commit()

        return jsonify({"message": "Planet added to favorites"}), 200
    except Exception as e:
        db.session.rollback() 
        return jsonify({"error": str(e)}), 500

@app.route("/favorite/people/<int:character_id>", methods=["POST"])
def add_character_to_favorites(character_id):
    try:

        data = request.get_json()
        user_id=data["user_id"]
        user_db = User.query.filter_by(id=user_id).first()
        if not user_db:
            return jsonify({"error": "User not found"}), 404
        
        if Favorites.query.filter_by(user_id=user_id, type_id=character_id,type=1).first():
            return jsonify({"error": "Character already added to favorites"}), 400

        db.session.add(Favorites(user_id=user_id, type_id=character_id,type=1))
        db.session.commit()

        return jsonify({"message": "Character added to favorites"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/favorite/planet/<int:planet_id>", methods=["DELETE"])
def delete_planet_from_favorites(planet_id):
    try:

        data = request.get_json()
        user_id=data["user_id"]
        user_db = User.query.filter_by(id=user_id).first()
        if not user_db:
            return jsonify({"error": "User not found"}), 404
        
        favorite_planet = Favorites.query.filter_by(user_id=user_id, type_id=planet_id,type=2).first()

        if favorite_planet:
            db.session.delete(favorite_planet)
            db.session.commit()
            return jsonify({"message": "Planet removed from favorites"}), 200

        return jsonify({"error": "Planet not found in favorites"}), 400
    except Exception as e:
        db.session.rollback() 
        return jsonify({"error": str(e)}), 500

@app.route("/favorite/people/<int:character_id>", methods=["DELETE"])
def delete_character_from_favorites(character_id):
    try:

        data = request.get_json()
        user_id=data["user_id"]
        user_db = User.query.filter_by(id=user_id).first()
        if not user_db:
            return jsonify({"error": "User not found"}), 404
        
        favorite_record = Favorites.query.filter_by(user_id=user_id, type_id=character_id,type=1).first()

        if favorite_record:
            db.session.delete(favorite_record)
            db.session.commit()
            return jsonify({"message": "Character removed from favorites"}), 200

        return jsonify({"error": "Character not found in favorites"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

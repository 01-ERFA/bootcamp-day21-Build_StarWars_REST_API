"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os, json
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Planet, Character, Film, Favorites
#from models import Person

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = "super-secret"  # Change this!
jwt = JWTManager(app)
 
# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@app.route("/login", methods=["POST"])
def login():   

    # consigue los datos del objeto del front
    email = request.json.get("email", None)
    password = request.json.get("password", None)

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"msg": "Bad email or password"}), 401
    elif email != user.email or password != user.password:
        return jsonify({"msg": "Bad email or password"}), 401

    # retorna un token
    access_token = create_access_token(identity=email)
    return jsonify({"user": {"id":str(user.id), "email": email}, "access_token":access_token})

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/profile", methods=["GET"])
@jwt_required() # el portero
def protected():
    # Access the identity of the current user with get_jwt_identity

    current_user = get_jwt_identity()
    user = User.query.filter_by(email=current_user).first()

    if user is None:
        return jsonify({"msg": "Bad email or password"}), 401

    response_body = {
        "name": str(user.name),
        "email": str(user.email),
        "id": str(user.id)
    }

    return jsonify(response_body), 200

@app.route("/valid-token", methods=["GET"])
@jwt_required()
def valid_token():  
    
    current_user = get_jwt_identity()
    login_user = User.query.filter_by(email=current_user).first()
    if login_user is None:
        return jsonify({"status": False}), 404
    response_body={
        "status": True,
        "user":{
            "name": str(login_user.name),
            "email": str(login_user.email),
            "id": str(login_user.id)
        }
    }
    return jsonify(response_body), 200

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

# seccion de los usuarios - metodo GET
@app.route('/users', methods=['GET']) # todos los usuarios
def get_users_all():

    all_users = User.query.all()
    results = list(map(lambda item: item.serialize(), all_users))
    return jsonify(results), 200
@app.route('/user/<int:user_id>', methods=['GET']) # solo un usuario segun la ID
def get_user(user_id):

    user = User.query.filter_by(id = user_id).first()
    # result = list(map(lambda item: item.serialize(), user))
    return jsonify(user.serialize()), 200

# seccion de los usuarios - metodo POST
@app.route('/users', methods=['POST'])
def create_user():
    # obtenemos lo que nos da el front
    body = json.loads(request.data)
    # consultamos a la tabla que guarda los datos del usuario si hay segun el email un usuario existente
    query_user = User.query.filter_by(email=body["email"]).first()
    favorites_user = Favorites.query.first()
    # si el email ingresado no existe en la tabla, crea al nuevo usuario
    if query_user is None:
        new_user = User(email=body["email"], password=body["password"], name=body["name"], is_active=bool(body["is_active"]), id=len(User.query.all())+1)
        db.session.add(new_user)
        db.session.commit()
        new_table_favorite = Favorites(list_favorites="", id=len(Favorites.query.all())+1)
        db.session.add(new_table_favorite)
        db.session.commit()
        # mensaje que vuelve al front
        response_body = {
            "msg": "created user"
        }
        return jsonify(response_body), 200
    # si el email si existe en la tabla, el mensaje que devuelve al front
    response_body = {
        "msg": "existed user"
    }
    return jsonify(response_body), 400

# los favoritos, segun el usuario
@app.route('/user/<int:user_id>/favorites', methods=['GET'])
def get_favorites(user_id):
    # obtener los favoritos segun el user_id, el user_id corresponde al ID de la tabla de favoritos.
    favorites_user = Favorites.query.filter_by(id = user_id).first()

    if favorites_user is None:
        obj = {
            "msg": "error; the user does not exist"
        }
        return jsonify(obj), 404
    obj = {
        "list_favorites": dict(favorites_user.serialize())["list_favorites"].split("$$")
    }
    return jsonify(obj), 200

# los favoritos - ¡¡PUT!!    + AGREGA y BORRA segun reciba el objeto del front... el objeto debe ser así {"favorite": "el favorito"} unicamente. 
@app.route('/user/<int:user_id>/favorites', methods=['PUT'])
def post_favorites(user_id):

    body = json.loads(request.data)
    
    
    favorites_user = Favorites.query.filter_by(id = user_id).first()
    
    if favorites_user is None:
        obj = {
            "msg": "error; the user does not exist"
        }
        return jsonify(obj), 404
    # borrar si ya esta en la lista 
    elif body["favorite"] in dict(favorites_user.serialize())["list_favorites"]:
        # conseguimos el str de la base de datos
        aux = dict(favorites_user.serialize())["list_favorites"]
        # eliminamos el valor usandolo de referencia de separación para crear un array
        aux = aux.split("$$"+body["favorite"])
        # convertimos el array sin el valor de vuelta en str, para mandarlo a la base de datos
        aux = ''.join(aux)
        favorites_user.list_favorites = aux
        db.session.commit()
        return jsonify({"msg": "the favorite has been deleted successfully"}), 200
    # mandar un error si no existe la lista o contenido en el body
    elif favorites_user is None and body is None:
        return jsonify({"msg": "There is no list for this user"}), 404

    # agregar si existe la lista pero no esta el contenido. 
    favorites_user.list_favorites = dict(favorites_user.serialize())["list_favorites"]+"$$"+body["favorite"]
    db.session.commit()
    return jsonify({"msg": "the favorite has been added successfully"})

# ver a los planetas - GET
@app.route('/planets', methods=['GET'])
def get_planets_all():
    all_planets = Planet.query.all()
    results = list(map(lambda item: item.serialize(), all_planets))
    return jsonify(results), 200
@app.route('/planet/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet = Planet.query.filter_by(id = planet_id).first()

    if planet is None:
        obj = {
            "msg": "error; the planet does not exist"
        }
        return jsonify(obj), 404

    return jsonify(planet.serialize())

# crear un planeta - POST
@app.route('/planets', methods=['POST'])
def create_planet():

    body = json.loads(request.data)

    query_planet = Planet.query.filter_by(name=body["name"]).first()


    if query_planet is None:
        new_planet = Planet(name=body["name"], id=len(User.query.all())+1, population=body["population"], rotation_period=body["rotation_period"], orbital_period=body["orbital_period"], diameter=body["diameter"], gravity=body["gravity"], terrain_grasslands=body["terrain_grasslands"], surface_water=body["surface_water"], climate=body["climate"])
        db.session.add(new_planet)
        db.session.commit()

        return jsonify({"msg": "created planet"})
 
    return jsonify({"msg": "existed planet"})

# eliminar un planeta - DELETE
@app.route('/planets', methods=['DELETE'])
def delete_planet():

    body = json.loads(request.data)
    print(body)
    # si el cuerpo no esta vacio
    if body is not None:
        key = "name"
        # si existe la propiedad "name" dentro del body
        if key in body:
            # hacemos la consulta a la tabla
            query_planet = Planet.query.filter_by(name=body["name"]).first()
            # si existe esa columna con ese "name"
            if query_planet is not None:
                # elimina dicha columna
                db.session.delete(query_planet)
                db.session.commit()
                return jsonify({"msg": "the planet was removed"}), 200
    #sino llega a pasar alguna de las condiciones anteriores, es porque ese planeta no esta en la tabla. 
    return jsonify({"msg": "planet not found"}), 404
 
@app.route('/characters', methods=['GET']) 
def get_characters_all():
    all_characters = Character.query.all()
    results = list(map(lambda item: item.serialize(), all_characters))
    return jsonify(results), 200
@app.route('/character/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character = Character.query.filter_by(id = character_id).first()

    if character is None:
        obj = {
            "msg": "error; the character does not exist"
        }
        return jsonify(obj), 404

    return jsonify(character.serialize()), 200

@app.route('/films', methods=['GET'])
def get_films_all():
    all_films = Film.query.all()
    results = list(map(lambda item: item.serialize(), all_films))
    return jsonify(results), 200
@app.route('/film/<int:film_id>', methods=['GET'])
def get_film(film_id):
    film = Film.query.filter_by(id = film_id).first()

    if film is None:
        obj = {
            "msg": "error; the film does not exist"
        }
        return jsonify(obj), 404

    return jsonify(film.serialize()), 200

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

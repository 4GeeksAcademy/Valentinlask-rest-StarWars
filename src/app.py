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
from models import db, User, Address, Planet, Character, Vehicle, FavoriteList
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import bcrypt




#from models import Person

app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'Test0_Key1'
jwt =  JWTManager(app)
bcrypt = Bcrypt(app)

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

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify(users=[user.serialize() for user in users])


@app.route('/users', methods=['POST'])
def create_user():
    data = request.get_json()
    id = data.get('id')
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')
    phone_number = data.get('phone_number')
    email = data.get('email')
    inscription_date = data.get('inscription_date')

    new_user = User(id = id, username=username, password=password, name=name,
                    phone_number=phone_number, email=email, inscription_date=inscription_date)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(message='User created successfully', user=new_user.serialize()), 200


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get(user_id)
    if user:
        return jsonify(user.serialize())
    else:
        return jsonify(message='User not found'), 404


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify(message='User not found'), 404

    data = request.get_json()
    user.username = data.get('username', user.username)
    user.password = data.get('password', user.password)
    user.name = data.get('name', user.name)
    user.phone_number = data.get('phone_number', user.phone_number)
    user.email = data.get('email', user.email)
    user.inscription_date = data.get('inscription_date', user.inscription_date)

    db.session.commit()

    return jsonify(message='User updated successfully', user=user.serialize())


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify(message='User deleted successfully')
    else:
        return jsonify(message='User not found'), 404


@app.route('/token', methods=['POST'])
def get_token():
  
    email = request.json.get('email')
    password = request.json.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    login_user = User.query.filter_by(email = request.json['email']).one()
    password_db = login_user.password
    true_o_false = bcrypt.check_password_hash(password_db, password)

    if true_o_false:
        user_id = login_user.id
        access_token = create_access_token(identity=user_id)
        return {'access_token': access_token}, 200
    
    else:
        return{'Error': 'Icorrect password0'}




@app.route('/addresses')
def get_addresses():
    addresses = Address.query.all()
    return jsonify(addresses=[address.serialize() for address in addresses])


@app.route('/planets')
def get_planets():
    planets = Planet.query.all()
    return jsonify(planets=[planet.serialize() for planet in planets])

@app.route('/planets', methods=['POST'])
def create_planet():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    size = data.get('size')

    new_planet = Planet(name=name, description=description, size=size)
    db.session.add(new_planet)
    db.session.commit()

    return jsonify(message='Planet created successfully', planet=new_planet.serialize()), 201


@app.route('/planets/<int:planet_id>', methods=['DELETE'])
def delete_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message='Planet deleted successfully')
    else:
        return jsonify(message='Planet not found'), 404


@app.route('/characters')
def get_characters():
    characters = Character.query.all()
    return jsonify(characters=[character.serialize() for character in characters])

@app.route('/characters', methods=['POST'])
def create_character():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    age = data.get('age')
    weapon = data.get('weapon')

    new_character = Character(name=name, description=description, age=age, weapon=weapon)
    db.session.add(new_character)
    db.session.commit()

    return jsonify(message='Character created successfully', character=new_character.serialize()), 201


@app.route('/characters/<int:character_id>', methods=['DELETE'])
def delete_character(character_id):
    character = Character.query.get(character_id)
    if character:
        db.session.delete(character)
        db.session.commit()
        return jsonify(message='Character deleted successfully')
    else:
        return jsonify(message='Character not found'), 404


@app.route('/vehicles')
def get_vehicles():
    vehicles = Vehicle.query.all()
    return jsonify(vehicles=[vehicle.serialize() for vehicle in vehicles])


@app.route('/vehicles', methods=['POST'])
def create_vehicle():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    age = data.get('age')
    weapon = data.get('weapon')

    new_vehicle = Vehicle(name=name, description=description, age=age, weapon=weapon)
    db.session.add(new_vehicle)
    db.session.commit()

    return jsonify(message='Vehicle created successfully', vehicle=new_vehicle.serialize()), 201


@app.route('/favorite-lists')
def get_favorite_lists():
    favorite_lists = FavoriteList.query.all()
    return jsonify(favorite_lists=[favorite_list.serialize() for favorite_list in favorite_lists])


@app.route('/favorite-lists', methods=['POST'])
def create_favorite_list():
    data = request.get_json()
    planet_id = data.get('planet_id')
    character_id = data.get('character_id')
    vehicle_id = data.get('vehicle_id')
    user_id = data.get('user_id')

    new_favorite_list = FavoriteList(planet_id=planet_id, character_id=character_id,
                                     vehicle_id=vehicle_id, user_id=user_id)
    db.session.add(new_favorite_list)
    db.session.commit()

    return jsonify(message='Favorite list created successfully', favorite_list=new_favorite_list.serialize()), 201


@app.route('/favorite-lists/<int:favorite_list_id>', methods=['DELETE'])
def delete_favorite_list(favorite_list_id):
    favorite_list = FavoriteList.query.get(favorite_list_id)
    if favorite_list:
        db.session.delete(favorite_list)
        db.session.commit()
        return jsonify(message='Favorite list deleted successfully')
    else:
        return jsonify(message='Favorite list not found'), 404

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

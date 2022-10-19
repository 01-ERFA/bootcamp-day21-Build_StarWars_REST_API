from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    favorites = db.relationship('Favorites', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "favorites": list(map(lambda item: item.serialize(), self.favorites))
            # do not serialize the password, its a security breach
        }
class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    population = db.Column(db.String(120), unique=True, nullable=False)
    rotation_period = db.Column(db.String(120), unique=True, nullable=False)
    orbital_period = db.Column(db.String(120), unique=True, nullable=False)
    diameter = db.Column(db.String(120), unique=True, nullable=False)
    gravity = db.Column(db.String(120), unique=True, nullable=False)
    terrain_grasslands = db.Column(db.String(120), unique=True, nullable=False)
    surface_water = db.Column(db.String(120), unique=True, nullable=False)
    climate = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return 'Planet %r' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "rotation_period": self.rotation_period,
            "orbital_period": self.orbital_period,
            "diameter": self.diameter,
            "gravity": self.gravity,
            "terrain_grasslands": self.terrain_grasslands,
            "surface_water": self.surface_water,
            "climate": self.climate
        }
class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    birth_year = db.Column(db.String(120), unique=True, nullable=False)
    species = db.Column(db.String(120), unique=True, nullable=False)
    height = db.Column(db.String(120), unique=True, nullable=False)
    mass = db.Column(db.String(120), unique=True, nullable=False)
    gender = db.Column(db.String(120), unique=True, nullable=False)
    hair_color = db.Column(db.String(120), unique=True, nullable=False)
    skin_color = db.Column(db.String(120), unique=True, nullable=False)
    homeWorld = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return 'Character %r' % self.id
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "birth_year": self.birth_year,
            "species": self.species,
            "height": self.height,
            "mass": self.mass,
            "gender": self.gender,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "homeWorld": self.homeWorld,
        }
class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    date_created = db.Column(db.String(120), unique=True, nullable=False)
    director = db.Column(db.String(120), unique=True, nullable=False)
    producers = db.Column(db.String(120), unique=True, nullable=False)
    opening_crawl = db.Column(db.String(700), unique=True, nullable=False)

    def __repr__(self):
        return 'Film %r' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "date_created": self.date_created,
            "director": self.director,
            "producers": self.producers,
            "opening_crawl": self.opening_crawl,
        }

class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    list_favorites = db.Column(db.String(700), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __repr__(self):
        return 'Favorites %r' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "list_favorites": self.list_favorites
        }
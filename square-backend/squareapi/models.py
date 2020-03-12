from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
db = SQLAlchemy()

class User(db.Model):
    """
    A user with a unique name.
    The password is only stored as hash (we do not salt currently).
    A user can own multiple skills.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    skills = db.relationship("Skill", backref="users")

    def __init__(self, name, password):
        self.name = name
        self.password_hash = generate_password_hash(password, method="sha256")

    @classmethod
    def authenticate(cls, username, password):
        if not username or not password:
            return None
        user = cls.query.filter_by(name=username).first()
        if not user or not check_password_hash(user.password_hash, password):
            return None
        return user

    def to_dict(self):
        return dict(id=self.id, name=self.name)

class Skill(db.Model):
    """
    A skill with a unique name.
    It belongs to one user.
    It should be only visible to this user or to all if published.
    The URL is not validated by us.
    """
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    name = db.Column(db.String(50), nullable=False, unique=True)
    is_published = db.Column(db.Boolean, nullable=False)
    url = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)

    def __init__(self, user, skill):
        self.owner_id = user["id"]
        self.name = skill["name"]
        self.is_published = False  # skill["is_published"]
        self.description = skill["description"]
        url = skill["url"]
        if url[-1] == "/":
            url = url[:-1]
        self.url = url

    def update(self, skill):
        self.name = skill["name"]
        # self.is_published = skill["is_published"]
        self.description = skill["description"]
        url = skill["url"]
        if url[-1] == "/":
            url = url[:-1]
        self.url = url

    def set_publish(self, new_status):
        self.is_published = new_status

    def to_dict(self):
        return dict(id=self.id, name=self.name, owner_id=self.owner_id, is_published=self.is_published,
                    description=self.description, url=self.url)
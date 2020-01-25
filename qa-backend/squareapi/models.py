from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    plaintext_pw = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return dict(id=self.id, name=self.name, plaintext_pw=self.plaintext_pw)

class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    def to_dict(self):
        return dict(id=self.id, name=self.name, owner_id=self.owner_id)
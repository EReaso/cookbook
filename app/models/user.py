# from flask_login import UserMixin
#
# from app.extensions import db
#
#
# class User(db.Model, UserMixin):
# 	id = db.Column(db.Integer, primary_key=True)
# 	username = db.Column(db.String(50), nullable=False)
# 	password = db.Column(db.Text, nullable=False)
# 	recipes = db.relationship('recipe', backref='user', lazy='dynamic')

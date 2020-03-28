from flask import Blueprint, jsonify, request
import db_session
from __all_models import User
import datetime

blueprint = Blueprint('users_api', __name__, template_folder='templates')


def check_new_user():
    sesion = db_session.create_session()
    if 'email' in request.json and sesion.query(User).filter(User.id == request.json['email']).first():
        return 'email already exists'
    if 'age' in request.json and not isinstance(request.json['age'], int):
        return 'bad age'
    if 'username' in request.json and sesion.query(User).filter(User.username == request.json['username']).first():
        return 'username already exists'
    if 'password' in request.json and len(request.json['password']) < 3:
        return 'bad password'
    return 'OK'


@blueprint.route('/api/users', methods=['GET'])
def get_users():
    sesion = db_session.create_session()
    users = sesion.query(User).all()
    sesion.close()
    return jsonify({'users': [user.to_dict(rules=('-id', '-hashed_password')) for user in users]})


@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    sesion = db_session.create_session()
    user = sesion.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'user not found'})
    sesion.close()
    return jsonify({'user': user.to_dict(rules=('-id', '-hashed_password'))})


@blueprint.route('/api/users', methods=['POST'])
def new_user():
    req_keys = [el.name for el in User.__table__.columns if el.name not in ['id', 'hashed_password', 'modified_date']]
    if not all([key in request.json for key in req_keys]) or not request.json:
        return jsonify({'error': 'bad request'})
    error = check_new_user()
    if error != 'OK':
        return jsonify({'error': error})
    user = User(surname=request.json['surname'],
                name=request.json['name'],
                age=request.json['age'],
                position=request.json['position'],
                speciality=request.json['speciality'],
                address=request.json['address'],
                email=request.json['email'],
                username=request.json['username'],
                modified_date=datetime.datetime.now())
    user.set_password(request.json['password'])
    sesion = db_session.create_session()
    sesion.add(user)
    sesion.commit()
    sesion.close()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    sesion = db_session.create_session()
    user = sesion.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'no such user'})
    sesion.delete(user)
    sesion.commit()
    sesion.close()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/users/<int:user_id>', methods=['PATCH'])
def edit_user(user_id):
    sesion = db_session.create_session()
    user = sesion.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'no such user'})
    if not request.json:
        return jsonify({'error': 'bad request'})
    error = check_new_user()
    if error != 'OK':
        return jsonify({'error': error})
    for key in request.json:
        if hasattr(user, key):
            if key == 'password':
                user.set_password(request.json['password'])
            else:
                setattr(user, key, request.json[key])
        else:
            return jsonify({'error': f'no column called {key}'})
    sesion.commit()
    sesion.close()
    return jsonify({'success': 'OK'})

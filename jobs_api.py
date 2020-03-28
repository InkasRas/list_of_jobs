from flask import Blueprint, jsonify, request
import db_session
from __all_models import Jobs, User
from datetime import datetime

blueprint = Blueprint('jobs_api', __name__, template_folder='templates')


def job_to_dict(job):
    dic = {}
    for c in job.__class__.__table__.columns:
        v = getattr(job, c.name)
        try:
            dic[c.name] = v
        except Exception:
            pass
    return dic


@blueprint.route('/api/jobs', methods=['GET'])
def get_jobs():
    sesion = db_session.create_session()
    jobs = sesion.query(Jobs).all()
    return jsonify({'response': 200, 'jobs': [job_to_dict(job) for job in jobs]})


@blueprint.route('/api/jobs/<int:job_id>', methods=['DELETE'])
def delete_job(job_id):
    sesion = db_session.create_session()
    job = sesion.query(Jobs).get(job_id)
    if not job:
        return jsonify({'error': 'job not found'})
    sesion.delete(job)
    sesion.commit()
    sesion.close()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/jobs/<int:job_id>', methods=['PATCH'])
def edit_job(job_id):
    sesion = db_session.create_session()
    job = sesion.query(Jobs).get(job_id)
    if not job:
        return jsonify({'error': 'job not found'})
    if not request.json:
        return jsonify({'error': 'no params'})
    for key in request.json:
        if hasattr(job, key):
            setattr(job, key, request.json[key])
        else:
            return jsonify({'error': f'no column called "{key}"'})
    sesion.commit()
    sesion.close()
    return jsonify({'success': 'OK'})


@blueprint.route('/api/jobs', methods=['POST'])
def add_job():
    if not request.json:
        return jsonify({'error': 'Emty request'})
    req_keys = [el.name for el in Jobs.__table__.columns if el.name not in ['id', 'end_date', 'start_date']]
    if not all([key in request.json for key in req_keys]):
        return jsonify({'error': 'Bad json'})
    sesion = db_session.create_session()
    if not sesion.query(User).filter(User.id == request.json['creator_id']).first():
        return jsonify({'error': 'creator not found'})
    if not sesion.query(User).filter(User.id == request.json['team_leader']).first():
        return jsonify({'error': 'team leader not found'})
    if not isinstance(request.json['work_size'], float) or request.json['work_size'] <= 0:
        return jsonify({'error': 'bad work size'})

    job = Jobs(
        collaborators=request.json['collaborators'],
        creator_id=int(request.json['creator_id']),
        is_finished=request.json['is_finished'],
        work_size=request.json['work_size'],
        team_leader=request.json['team_leader'],
        job=request.json['job'],
        start_date=datetime.fromisoformat(request.json['start_date'])
    )
    sesion.add(job)
    sesion.commit()
    sesion.close()
    return jsonify({'succes': 'OK'})


@blueprint.route('/api/jobs/<job_id>', methods=['GET'])
def get_job(job_id):
    try:
        job_id = int(job_id)
    except Exception:
        return jsonify({'error': 'job id not int'})
    sesion = db_session.create_session()
    job = sesion.query(Jobs).filter(Jobs.id == job_id).first()
    sesion.close()
    if not job:
        return jsonify({'error': 'job not found'})
    else:
        return jsonify({'response': 200, 'job': job_to_dict(job)})

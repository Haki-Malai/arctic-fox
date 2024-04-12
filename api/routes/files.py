from flask import Blueprint, abort
from apifairy import authenticate, body, response, other_responses

from api import db, aws_wrapper
from api.models import File
from api.schemas import FileSchema, EmptySchema, PresignedPostSchema
from api.auth import token_auth
from api.enums import Role

from typing import List

bp = Blueprint('file', __name__)
file_schema = FileSchema()
files_schema = FileSchema(many=True)
update_file_schema = FileSchema(partial=True)
presigned_post_schema = PresignedPostSchema()


@bp.route('/file/pre', methods=['POST'])
@authenticate(token_auth)
@body(presigned_post_schema)
@response(presigned_post_schema, 201)
def pre(data: dict) -> dict:
    """Retrieve a pre-signed URL for uploading a file"""
    return aws_wrapper.generate_presigned_post(**data)


@bp.route('/file/<int:id>', methods=['GET'])
@authenticate(token_auth)
@response(file_schema)
@other_responses({404: 'File not found'})
def get(id: int) -> File:
    """Retrieve file by id"""
    return db.session.get(File, id) or abort(404)


@bp.route('/files', methods=['GET'])
@authenticate(token_auth)
@response(files_schema)
def all() -> List[File]:
    """Retrieve all files"""
    return db.session.scalars(File.select()).all()


@bp.route('/videos', methods=['GET'])
@authenticate(token_auth)
@response(files_schema)
def videos() -> List[File]:
    """Retrieve all videos"""
    return db.session.scalars(
        File.select().where(File.mimetype == 'video/mp4')).all()


@bp.route('/images', methods=['GET'])
@authenticate(token_auth)
@response(files_schema)
def images() -> List[File]:
    """Retrieve all images"""
    return db.session.scalars(File.select().where(
        File.mimetype.in_(['image/jpeg', 'image/png', 'image/gif']))).all()


@bp.route('/file', methods=['POST'])
@authenticate(token_auth, role=[Role.ADMIN.name, Role.MODERATOR.name])
@body(file_schema)
@response(file_schema, 201)
def post(args) -> File:
    """Create a new file"""
    user = token_auth.current_user()
    file = file(created_by=user.id, **args)
    db.session.add(file)
    db.session.commit()

    return file


@bp.route('/file/<int:id>', methods=['PUT'])
@authenticate(token_auth, role=[Role.ADMIN.name, Role.MODERATOR.name])
@body(update_file_schema)
@response(file_schema)
@other_responses({404: 'File not found'})
def put(data, id) -> File:
    """Edit a file"""
    file = db.session.get(file, id) or abort(404)
    file.update(data)
    db.session.commit()
    return file


@bp.route('/file/<int:id>', methods=['DELETE'])
@authenticate(token_auth, role=[Role.ADMIN.name, Role.MODERATOR.name])
@response(EmptySchema, 204)
@other_responses({404: 'File not found'})
def delete(id) -> dict:
    """Delete a file"""
    file = db.session.get(file, id) or abort(404)
    db.session.delete(file)
    db.session.commit()
    return {}

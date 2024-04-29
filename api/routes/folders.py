from flask import Blueprint, abort
from apifairy import authenticate, body, response, other_responses

from api import db
from api.models import Role, Folder
from api.schemas import FolderSchema, EmptySchema
from api.auth import token_auth

from typing import List, Dict, Any

bp = Blueprint('folders', __name__)
folder_schema = FolderSchema()
folders_schema = FolderSchema(many=True)
update_folder_schema = FolderSchema(partial=True)


@bp.route('/folders/<int:id>', methods=['GET'])
@authenticate(token_auth)
@response(folder_schema)
@other_responses({404: 'Folder not found'})
def get(id: int) -> Folder:
    """Retrieve folder by id"""
    return db.session.get(Folder, id) or abort(404)


@bp.route('/folders', methods=['GET'])
@authenticate(token_auth)
@response(folders_schema)
def all() -> List[Folder]:
    """Retrieve all folders"""
    return db.session.scalars(Folder.select()).all()


@bp.route('/folders', methods=['POST'])
@authenticate(token_auth, role=[Role.ADMIN.name, Role.MODERATOR.name])
@body(folder_schema)
@response(folder_schema, 201)
def post(data: Dict) -> Folder:
    """Create a new folder"""
    user = token_auth.current_user()
    folder = Folder(created_by=user.id, **data)
    db.session.add(folder)
    db.session.commit()

    return folder


@bp.route('/folders/<int:id>', methods=['PUT'])
@authenticate(token_auth, role=[Role.ADMIN.name, Role.MODERATOR.name])
@body(update_folder_schema)
@response(folder_schema)
@other_responses({404: 'Folder not found'})
def put(data: Dict, id: int) -> Folder:
    """Edit a folder"""
    folder = db.session.get(Folder, id) or abort(404)
    folder.update(data)
    db.session.commit()
    return folder


@bp.route('/folders/<int:id>', methods=['DELETE'])
@authenticate(token_auth, role=[Role.ADMIN.name, Role.MODERATOR.name])
@response(EmptySchema, 204)
@other_responses({404: 'Folder not found'})
def delete(id: int) -> Dict[str, Any]:
    """Delete a folder"""
    folder = db.session.get(Folder, id) or abort(404)
    db.session.delete(folder)
    db.session.commit()
    return {}

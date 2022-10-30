from flask import Blueprint, abort
from apifairy import authenticate, response, other_responses
from api import db
from api.models import Notification
from api.schemas import NotificationSchema, DateTimePaginationSchema, EmptySchema
from api.auth import token_auth
from api.decorators import paginated_response

notifications = Blueprint('notifications', __name__)
notification_schema = NotificationSchema()
notifications_schema = NotificationSchema(many=True)
update_notification_schema = NotificationSchema(partial=True)


@notifications.route('/<int:id>')
@authenticate(token_auth)
@paginated_response(notifications_schema,
                    order_by=Notification.timestamp,
                    order_direction='desc',
                    pagination_schema=DateTimePaginationSchema)
def get_notification(notification_id):
    """Retrieve a notification by id.
    
    This endpoint requires authentication and uses pagination.
    """
    notification = db.session.get(Notification, notification_id) or abort(404)
    if token_auth.current_user().id == notification.user_id:
        notification.read = True
        db.session.commit()
        return notification

    
@notifications.route('/<int:id>', methods=['DELETE'])
@authenticate(token_auth)
@response(EmptySchema, status_code=204,
          description='Notification successfully deleted.')
@other_responses({404: 'Comment not found', 403: 'Not allowed to delete the post'})
def delete_notification(notification_id):
    """Delete a notification.
    
    This endpoint requires authentication.
    """
    notification = db.session.get(Notification, notification_id) or abort(404)
    if token_auth.current_user().id != notification.user_id:
        abort(403)
    notification.read = True
    db.session.commit()
    return {}
    

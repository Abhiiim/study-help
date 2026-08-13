from sqlalchemy.orm import Session

from app.models.activity import Activity


def log_activity(db: Session, resource_id: int, event_type: str) -> Activity:
    activity = Activity(resource_id=resource_id, event_type=event_type)
    db.add(activity)
    return activity

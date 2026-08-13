from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.collection import Collection
from app.models.resource import Resource
from app.models.tag import Tag


def get_resource(db: Session, user_id: int, resource_id: int) -> Resource | None:
    return db.scalar(
        select(Resource)
        .options(selectinload(Resource.tags), selectinload(Resource.collections))
        .where(and_(Resource.id == resource_id, Resource.user_id == user_id))
    )


def get_resource_using_url(db: Session, user_id: int, url: str) -> Resource | None:
    return db.scalar(
        select(Resource)
        .options(selectinload(Resource.tags), selectinload(Resource.collections))
        .where(and_(Resource.url == url, Resource.user_id == user_id))
    )


def list_resources(
    db: Session,
    user_id: int,
    *,
    search: str | None,
    platform: str | None,
    resource_type: str | None,
    collection_id: int | None,
    tag_id: int | None,
    page: int,
    limit: int,
) -> tuple[list[Resource], int]:
    filters = [Resource.user_id == user_id, Resource.is_deleted == False]

    if platform:
        filters.append(Resource.platform == platform.strip().lower())
    if resource_type:
        filters.append(Resource.type == resource_type.strip().lower())
    if collection_id is not None:
        filters.append(Resource.collections.any(Collection.id == collection_id))
    if tag_id is not None:
        filters.append(Resource.tags.any(Tag.id == tag_id))

    count_query = select(func.count(func.distinct(Resource.id))).select_from(Resource)
    list_query = select(Resource).options(selectinload(Resource.tags), selectinload(Resource.collections))

    if search:
        search_text = f"%{search.strip()}%"
        search_filter = or_(
            Resource.title.ilike(search_text),
            Resource.domain.ilike(search_text),
            Tag.name.ilike(search_text),
            Collection.name.ilike(search_text),
        )
        count_query = count_query.outerjoin(Resource.tags).outerjoin(Resource.collections)
        list_query = list_query.outerjoin(Resource.tags).outerjoin(Resource.collections)
        filters.append(search_filter)

    count_query = count_query.where(*filters)
    list_query = list_query.where(*filters).distinct()

    total = db.scalar(count_query) or 0
    offset = (page - 1) * limit
    items = list(
        db.scalars(
            list_query.order_by(Resource.created_at.desc()).offset(offset).limit(limit)
        ).all()
    )
    return items, total


def get_collection(db: Session, user_id: int, collection_id: int) -> Collection | None:
    return db.scalar(
        select(Collection).where(and_(Collection.id == collection_id, Collection.user_id == user_id))
    )


def list_collections(db: Session, user_id: int) -> list[Collection]:
    return list(
        db.scalars(select(Collection)
        .where(and_(Collection.user_id == user_id, Collection.is_deleted == False))
        .order_by(Collection.created_at.desc())
    ).all())


def get_tag(db: Session, tag_id: int) -> Tag | None:
    return db.get(Tag, tag_id)


def list_tags(db: Session) -> list[Tag]:
    return list(db.scalars(select(Tag).order_by(Tag.name.asc())).all())


def get_tags_by_ids(db: Session, tag_ids: list[int]) -> list[Tag]:
    if not tag_ids:
        return []
    return list(db.scalars(select(Tag).where(Tag.id.in_(tag_ids))).all())


def get_collections_by_ids(db: Session, user_id: int, collection_ids: list[int]) -> list[Collection]:
    if not collection_ids:
        return []
    return list(
        db.scalars(
            select(Collection).where(and_(Collection.user_id == user_id, Collection.id.in_(collection_ids)))
        ).all()
    )

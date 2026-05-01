from sqlalchemy import and_, asc, desc, func, or_, select
from sqlalchemy.orm import Session

from app.api.core.exceptions import NotFoundError
from app.models.saved_item import SavedItem
from app.models.user import User
from app.parsers.service import parse_url
from app.schemas.item import ItemCreateRequest, ItemUpdateRequest


def _clean_tags(tags: list[str]) -> list[str]:
    cleaned: list[str] = []
    for raw in tags:
        value = raw.strip()
        if value and value not in cleaned:
            cleaned.append(value[:50])
    return cleaned


def save_item(db: Session, user: User, payload: ItemCreateRequest) -> SavedItem:
    parser_result = parse_url(str(payload.url))

    existing_item = db.scalar(
        select(SavedItem).where(
            and_(
                SavedItem.user_id == user.id,
                SavedItem.canonical_url == parser_result.canonical_url,
            )
        )
    )

    cleaned_tags = _clean_tags(payload.tags)

    if existing_item is not None:
        existing_item.url = str(payload.url)
        existing_item.source_site = parser_result.source_site
        existing_item.content_type = parser_result.content_type
        existing_item.title = parser_result.title
        existing_item.snippet = parser_result.snippet
        existing_item.metadata_json = parser_result.metadata_json
        existing_item.is_favorite = payload.is_favorite
        existing_item.note = payload.note
        existing_item.tags = cleaned_tags
        db.commit()
        db.refresh(existing_item)
        return existing_item

    item = SavedItem(
        user_id=user.id,
        url=str(payload.url),
        canonical_url=parser_result.canonical_url,
        source_site=parser_result.source_site,
        content_type=parser_result.content_type,
        title=parser_result.title,
        snippet=parser_result.snippet,
        metadata_json=parser_result.metadata_json,
        is_favorite=payload.is_favorite,
        note=payload.note,
        tags=cleaned_tags,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def list_items(
    db: Session,
    user: User,
    q: str | None,
    source_site: str | None,
    content_type: str | None,
    is_favorite: bool | None,
    page: int,
    limit: int,
    sort: str,
) -> tuple[list[SavedItem], int]:
    filters = [SavedItem.user_id == user.id]

    if q:
        query_text = f"%{q.strip()}%"
        filters.append(
            or_(
                SavedItem.title.ilike(query_text),
                SavedItem.snippet.ilike(query_text),
                SavedItem.note.ilike(query_text),
                SavedItem.url.ilike(query_text),
            )
        )

    if source_site:
        filters.append(SavedItem.source_site == source_site.strip().lower())

    if content_type:
        filters.append(SavedItem.content_type == content_type)

    if is_favorite is not None:
        filters.append(SavedItem.is_favorite == is_favorite)

    total = db.scalar(select(func.count()).select_from(SavedItem).where(*filters)) or 0

    order_clause = desc(SavedItem.created_at) if sort == "recent" else asc(SavedItem.created_at)

    items = db.scalars(
        select(SavedItem)
        .where(*filters)
        .order_by(order_clause)
        .offset((page - 1) * limit)
        .limit(limit)
    ).all()

    return items, total


def get_item_or_404(db: Session, user: User, item_id: int) -> SavedItem:
    item = db.scalar(
        select(SavedItem).where(and_(SavedItem.id == item_id, SavedItem.user_id == user.id))
    )
    if item is None:
        raise NotFoundError("Saved item not found")
    return item


def update_item(db: Session, user: User, item_id: int, payload: ItemUpdateRequest) -> SavedItem:
    item = get_item_or_404(db, user, item_id)

    if payload.is_favorite is not None:
        item.is_favorite = payload.is_favorite
    if payload.note is not None:
        item.note = payload.note
    if payload.tags is not None:
        item.tags = _clean_tags(payload.tags)

    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, user: User, item_id: int) -> None:
    item = get_item_or_404(db, user, item_id)
    db.delete(item)
    db.commit()

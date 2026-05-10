from __future__ import annotations

from typing import Optional

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.db.models import Q

from .models import Users


def _is_encoded_password(value: str) -> bool:
    if not value:
        return False
    try:
        identify_hasher(value)
        return True
    except Exception:
        return False


def _build_unique_username(seed: str, exclude_pk: Optional[int] = None) -> str:
    user_model = get_user_model()
    username_field_name = user_model.USERNAME_FIELD
    username_field = user_model._meta.get_field(username_field_name)
    max_length = getattr(username_field, "max_length", 150) or 150

    base = (seed or "user").strip() or "user"
    base = base[:max_length]
    candidate = base
    suffix = 1

    while True:
        lookup = {f"{username_field_name}__iexact": candidate}
        qs = user_model._default_manager.filter(**lookup)
        if exclude_pk is not None:
            qs = qs.exclude(pk=exclude_pk)
        if not qs.exists():
            return candidate

        marker = f"_{suffix}"
        candidate = f"{base[: max_length - len(marker)]}{marker}"
        suffix += 1


def _match_auth_user(app_user: Users):
    user_model = get_user_model()
    username_field_name = user_model.USERNAME_FIELD
    email_field_name = user_model.get_email_field_name()

    username_value = (app_user.username or "").strip()
    email_value = (app_user.email or "").strip()

    query = Q(**{f"{username_field_name}__iexact": username_value})
    if email_value:
        query |= Q(**{f"{email_field_name}__iexact": email_value})
    return user_model._default_manager.filter(query).order_by("id").first()


def sync_app_user_to_auth(app_user: Users, raw_password: Optional[str] = None):
    """
    Keep one legacy app Users record in sync with Django auth user.
    """
    user_model = get_user_model()
    username_field_name = user_model.USERNAME_FIELD
    email_field_name = user_model.get_email_field_name()

    auth_user = _match_auth_user(app_user)
    if not auth_user:
        seed = (app_user.username or "").strip()
        if not seed and app_user.email:
            seed = app_user.email.split("@", 1)[0]
        if not seed:
            seed = f"user{app_user.pk}"
        username = _build_unique_username(seed)
        auth_user = user_model._default_manager.model()
        setattr(auth_user, username_field_name, username)

    changed = False
    desired_username = _build_unique_username(app_user.username, exclude_pk=auth_user.pk)
    if getattr(auth_user, username_field_name) != desired_username:
        setattr(auth_user, username_field_name, desired_username)
        changed = True

    desired_email = (app_user.email or "").strip()
    if getattr(auth_user, email_field_name, "") != desired_email:
        setattr(auth_user, email_field_name, desired_email)
        changed = True

    if auth_user.first_name != (app_user.first_name or ""):
        auth_user.first_name = app_user.first_name or ""
        changed = True
    if auth_user.last_name != (app_user.last_name or ""):
        auth_user.last_name = app_user.last_name or ""
        changed = True
    if auth_user.is_active != bool(app_user.is_active):
        auth_user.is_active = bool(app_user.is_active)
        changed = True

    app_password_to_store = None
    if raw_password:
        auth_user.set_password(raw_password)
        app_password_to_store = auth_user.password
        changed = True
    else:
        legacy_password = (app_user.password or "").strip()
        if legacy_password:
            if _is_encoded_password(legacy_password):
                if auth_user.password != legacy_password:
                    auth_user.password = legacy_password
                    changed = True
            else:
                auth_user.set_password(legacy_password)
                app_password_to_store = auth_user.password
                changed = True

    if changed or auth_user.pk is None:
        auth_user.save()

    if app_password_to_store and app_user.password != app_password_to_store:
        app_user.password = app_password_to_store
        app_user.save(update_fields=["password"])

    return auth_user


def sync_all_app_users_to_auth() -> None:
    for app_user in Users.objects.all().iterator():
        sync_app_user_to_auth(app_user)

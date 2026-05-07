from dataclasses import dataclass
from typing import Iterable, Optional

from django.db.models import Q, QuerySet

from .models import Branches, Users

ROLE_ADMIN = "admin"
ROLE_BRANCH_MANAGER = "branch_manager"
ROLE_USER = "user"
VALID_ROLES = {ROLE_ADMIN, ROLE_BRANCH_MANAGER, ROLE_USER}


@dataclass(frozen=True)
class AccessContext:
    app_user: Optional[Users]
    role: str
    assigned_branch_id: Optional[int]

    @property
    def is_admin(self) -> bool:
        return self.role == ROLE_ADMIN

    @property
    def is_branch_manager(self) -> bool:
        return self.role == ROLE_BRANCH_MANAGER

    @property
    def is_user(self) -> bool:
        return self.role == ROLE_USER

    @property
    def allowed_branch_ids(self) -> set[int]:
        if self.is_admin:
            return set()
        if self.assigned_branch_id:
            return {self.assigned_branch_id}
        return set()


def _is_django_admin(request) -> bool:
    user = getattr(request, "user", None)
    if not user or not user.is_authenticated:
        return False
    return bool(user.is_superuser or user.is_staff)


def get_request_app_user(request) -> Optional[Users]:
    if hasattr(request, "_app_user_cache"):
        return request._app_user_cache

    user = getattr(request, "user", None)
    app_user = None
    if user and user.is_authenticated:
        app_user = (
            Users.objects.select_related("assigned_branch")
            .filter(Q(username=user.username) | Q(email=user.email))
            .first()
        )

    request._app_user_cache = app_user
    return app_user


def get_access_context(request) -> AccessContext:
    cached = getattr(request, "_access_context_cache", None)
    if cached is not None:
        return cached

    app_user = get_request_app_user(request)
    if _is_django_admin(request):
        role = ROLE_ADMIN
    elif app_user and app_user.user_role in VALID_ROLES:
        role = app_user.user_role
    else:
        role = ROLE_USER

    assigned_branch_id = app_user.assigned_branch_id if app_user else None
    ctx = AccessContext(
        app_user=app_user,
        role=role,
        assigned_branch_id=assigned_branch_id,
    )
    request._access_context_cache = ctx
    return ctx


def get_role(request) -> str:
    return get_access_context(request).role


def has_any_branch_access(request) -> bool:
    access = get_access_context(request)
    return access.is_admin or bool(access.assigned_branch_id)


def can_access_branch(request, branch_id: Optional[int]) -> bool:
    if branch_id is None:
        return True
    access = get_access_context(request)
    if access.is_admin:
        return True
    return branch_id in access.allowed_branch_ids


def normalize_branch_id_for_user(request, requested_branch_id: Optional[int]) -> Optional[int]:
    access = get_access_context(request)
    if access.is_admin:
        return requested_branch_id
    if not access.assigned_branch_id:
        return None
    if requested_branch_id is None:
        return access.assigned_branch_id
    return requested_branch_id if requested_branch_id in access.allowed_branch_ids else None


def scope_branch_queryset(request, queryset: QuerySet, branch_field: str = "branch_id") -> QuerySet:
    access = get_access_context(request)
    if access.is_admin:
        return queryset
    if not access.allowed_branch_ids:
        return queryset.none()
    return queryset.filter(**{f"{branch_field}__in": list(access.allowed_branch_ids)})


def scope_branches_queryset(request, queryset: Optional[QuerySet] = None) -> QuerySet:
    qs = queryset if queryset is not None else Branches.objects.all()
    access = get_access_context(request)
    if access.is_admin:
        return qs.order_by("name")
    if not access.allowed_branch_ids:
        return qs.none()
    return qs.filter(id__in=list(access.allowed_branch_ids)).order_by("name")


def has_role(request, allowed_roles: Iterable[str]) -> bool:
    return get_role(request) in set(allowed_roles)

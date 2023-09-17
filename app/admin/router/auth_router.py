from typing import Annotated

from fastapi import APIRouter, Request, Depends, Security, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, func, delete
from sqlalchemy.orm import joinedload
from starlette import status
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates

from app.admin.service.auth_service import COOKIE_NAME, get_active_stuff_user
from app.api.model.user import UserLogin
from app.constant.application_enum import ScopeEnum
from app.core.security import get_password_hash
from app.db import orm
from app.db.database_engine import async_session
from app.service.impl.auth_service import AuthService

router = APIRouter()

templates = Jinja2Templates(directory="app/admin/templates")
auth_service = AuthService()


@router.get("/", response_class=HTMLResponse)
async def login(request: Request):
    context = {
        'request': request,
        'title': "Login"
    }
    return templates.TemplateResponse("login.html", context=context)


@router.post("/", response_class=HTMLResponse)
async def login_post(request: Request, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_login = UserLogin(
        username=form_data.username,
        password=form_data.password
    )
    user_token = await auth_service.login(user_login=user_login)
    response = RedirectResponse("/admin/dashboard", status.HTTP_302_FOUND)
    response.set_cookie(
        key=COOKIE_NAME,
        value=f"Bearer {user_token.access_token}"
    )
    return response


@router.get("/dashboard", response_class=HTMLResponse)
async def get_dashboard(request: Request, user: Annotated[orm.User, Security(get_active_stuff_user)]):
    context = {
        'request': request,
        'user': user
    }
    return templates.TemplateResponse("dashboard.html", context=context)


@router.get("/add-user", response_class=HTMLResponse)
async def get_add_user_form(request: Request, user: Annotated[orm.User, Security(get_active_stuff_user,
                                                                                 scopes=[ScopeEnum.USERS_CREATE,
                                                                                         ScopeEnum.ROLES_GET,
                                                                                         ScopeEnum.ROLES_GET_ALL])]):
    async with async_session() as session:
        stmt = select(orm.Role)
        roles = await session.execute(stmt)
        roles = list(roles.scalars())

    context = {
        'request': request,
        'title': "Add User",
        'user': user,
        'roles': roles
    }
    return templates.TemplateResponse("add_user.html", context=context)


@router.post("/add-user", response_class=HTMLResponse)
async def add_user(request: Request, user: Annotated[orm.User, Security(get_active_stuff_user,
                                                                        scopes=[ScopeEnum.USERS_CREATE,
                                                                                ScopeEnum.ROLES_GET,
                                                                                ScopeEnum.ROLES_GET_ALL])]):
    form_data = await request.form()
    roles = form_data.getlist("roles")

    new_user = orm.User(
        username=form_data.get('username'),
        password=get_password_hash(form_data.get('password')),
        email=form_data.get('email'),
        phone=form_data.get('phone'),
        first_name=form_data.get('first_name'),
        last_name=form_data.get('last_name'),
        is_active=True,
        is_super_user=False,
        is_staff=form_data.get('is_staff').lower() == "true"
    )

    async with async_session() as session:
        stmt = select(orm.User).filter(orm.User.username == new_user.username).limit(1)
        db_user = await session.execute(stmt)
        db_user = db_user.scalar_one_or_none()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Use different user name.",
            )

        session.add(new_user)
        await session.flush()
        await session.refresh(new_user)

        for role_id in roles:
            user_role_association = orm.UserRoleAssociation(
                user_id=new_user.id,
                role_id=int(role_id)
            )
            session.add(user_role_association)

        await session.commit()

    return RedirectResponse("/admin/users", status.HTTP_302_FOUND)


@router.get("/users", response_class=HTMLResponse)
async def get_users(request: Request,
                    user: Annotated[orm.User, Security(get_active_stuff_user, scopes=[ScopeEnum.USERS_GET_ALL])]):
    async with async_session() as session:
        stmt = select(orm.User)
        users = await session.execute(stmt)
        users = list(users.scalars())

    content_list = enumerate(users, start=1)

    context = {
        'request': request,
        'user': user,
        'content_type': "User",
        'content_list': content_list
    }
    return templates.TemplateResponse("users_list.html", context=context)


@router.get("/roles", response_class=HTMLResponse)
async def get_roles(request: Request,
                    user: Annotated[orm.User, Security(get_active_stuff_user, scopes=[ScopeEnum.ROLES_GET_ALL])]):
    async with async_session() as session:
        stmt = select(orm.Role)
        roles = await session.execute(stmt)
        roles = list(roles.scalars())

    content_list = enumerate(roles, start=1)

    context = {
        'request': request,
        'user': user,
        'content_type': "Role",
        'content_list': content_list
    }
    return templates.TemplateResponse("generic_content.html", context=context)


@router.get("/add-role", response_class=HTMLResponse)
async def get_role_form(request: Request, user: Annotated[
    orm.User, Security(get_active_stuff_user, scopes=[ScopeEnum.ROLES_CREATE, ScopeEnum.PERMISSIONS_GET_ALL])]):
    async with async_session() as session:
        stmt = select(
            func.row(orm.ContentType.id, orm.ContentType.name).label('contain_types'),
            func.array_agg(func.row(orm.Permission.id, orm.Permission.name)).label('permissions')
        ).join_from(
            orm.ContentType,
            orm.Permission,
            orm.ContentType.id == orm.Permission.content_type_id
        ).group_by(
            orm.ContentType.id
        ).order_by(
            orm.ContentType.id
        )

        permission_groups = await session.execute(stmt)
        permission_groups = permission_groups.all()

    context = {
        'request': request,
        'permission_groups': permission_groups
    }
    return templates.TemplateResponse("add_role.html", context=context)


@router.post("/add-role", response_class=HTMLResponse)
async def add_role(request: Request, user: Annotated[
    orm.User, Security(get_active_stuff_user, scopes=[ScopeEnum.ROLES_CREATE, ScopeEnum.PERMISSIONS_GET_ALL])]):
    form_data = await request.form()
    permissions = form_data.getlist("permissions")

    new_role = orm.Role(
        name=form_data.get('role_name').upper()
    )

    async with async_session() as session:
        stmt = select(orm.Role).filter(orm.Role.name == new_role.name).limit(1)
        db_role = await session.execute(stmt)
        db_role = db_role.scalar_one_or_none()
        if db_role:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Use different role name.",
            )

        session.add(new_role)
        await session.flush()
        await session.refresh(new_role)

        for p_id in permissions:
            new_permission = orm.RolePermissionAssociation(
                role_id=new_role.id,
                permission_id=int(p_id)
            )
            session.add(new_permission)

        await session.commit()

    return RedirectResponse("/admin/roles", status.HTTP_302_FOUND)


@router.get("/edit-role/{role_id}", response_class=HTMLResponse)
async def get_edit_role(request: Request, role_id: int, user: Annotated[
    orm.User, Security(get_active_stuff_user, scopes=[ScopeEnum.ROLES_UPDATE, ScopeEnum.PERMISSIONS_GET_ALL])]):
    async with async_session() as session:
        stmt = select(orm.Role).where(orm.Role.id == role_id).options(joinedload(orm.Role.permissions))
        role = await session.execute(stmt)
        role = role.scalars().first()

        stmt = select(
            func.row(orm.ContentType.id, orm.ContentType.name).label('contain_types'),
            func.array_agg(func.row(orm.Permission.id, orm.Permission.name)).label('permissions')
        ).join_from(
            orm.ContentType,
            orm.Permission,
            orm.ContentType.id == orm.Permission.content_type_id
        ).group_by(
            orm.ContentType.id
        ).order_by(
            orm.ContentType.id
        )

        permission_groups = await session.execute(stmt)
        permission_groups = permission_groups.all()

    selected_permissions = set([p.id for p in role.permissions])

    context = {
        'request': request,
        'role': role,
        'permission_groups': permission_groups,
        'selected_permissions': selected_permissions
    }
    return templates.TemplateResponse("edit_role.html", context=context)


@router.post("/edit-role/{role_id}", response_class=HTMLResponse)
async def edit_role(request: Request, role_id: int, user: Annotated[
    orm.User, Security(get_active_stuff_user, scopes=[ScopeEnum.ROLES_UPDATE, ScopeEnum.PERMISSIONS_GET_ALL])]):
    form_data = await request.form()
    permissions = form_data.getlist("permissions")

    async with async_session() as session:
        stmt = select(orm.Role).where(orm.Role.id == role_id).options(joinedload(orm.Role.permissions))
        db_role = await session.execute(stmt)
        db_role = db_role.scalars().first()

        selected_permissions = set([p.id for p in db_role.permissions])
        permissions = set([int(p_id) for p_id in permissions])

        for p_id in permissions:
            if p_id not in selected_permissions:
                new_permission = orm.RolePermissionAssociation(
                    role_id=db_role.id,
                    permission_id=int(p_id)
                )
                session.add(new_permission)

        for p_id in selected_permissions:
            if p_id not in permissions:
                stmt = delete(orm.RolePermissionAssociation).where(orm.RolePermissionAssociation.role_id == role_id,
                                                                   orm.RolePermissionAssociation.permission_id == p_id)
                await session.execute(stmt)

        await session.commit()

    return RedirectResponse("/admin/roles", status.HTTP_302_FOUND)

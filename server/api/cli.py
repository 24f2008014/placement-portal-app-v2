import click
from flask import Blueprint
from api import db
from api.models import User, Role

# Flask docs: "cli_group=None removes the nesting & merges the commands directly to the application's level". 
# This allows commands to be run as `flask <command>` instead of `flask cli <command>`.
bp = Blueprint('cli', __name__, cli_group=None)

@bp.cli.command('create-role')
@click.argument('name')
def create_role(name):
    """Adds the specified role to the `Role` table."""
    role = db.session.execute(db.select(Role).where(Role.name == name)).scalar_one_or_none() # .first() returns a row object, not the actual ORM object
    if role is None:
        role = Role(name=name)
        db.session.add(role)
        click.echo(f"'{name}' role added to 'Role' table.")
        db.session.commit()
    else:
        click.echo(f"'{name}' role already exists in 'Role' table.")
    

@bp.cli.command('create-admin')
@click.pass_context
def create_admin(ctx):
    """
    Creates the `admin` role in the `Role` table, if it does not exist.

    Creates an admin account in the `User` table, if one does not exist, with the following credentials:
    
    EMAIL: `24f2008014@ds.study.iitm.ac.in`
    PASSWORD: `12345678`
    """
    admin_role = db.session.execute(db.select(Role).where(Role.name == "admin")).scalar_one_or_none()
    if admin_role is None:
        ctx.invoke(create_role, name="admin") # can't just call the function directly. need to pass the context first.
    
    admin_user = db.session.execute(db.select(User).where(User.email == "24f2008014@ds.study.iitm.ac.in")).scalar_one_or_none()
    if admin_user is None:
        admin_role = db.session.execute(db.select(Role).where(Role.name == "admin")).scalar_one_or_none()
        admin_user = User(email="24f2008014@ds.study.iitm.ac.in", roles=[admin_role])
        admin_user.set_password("12345678")
        db.session.add(admin_user)
        click.echo("admin user added to 'User' table. Email: 24f2008014@ds.study.iitm.ac.in // Password: 12345678")
    else:
        click.echo("admin user already exists in 'User' table.")
    db.session.commit()

@bp.cli.command('setup-db')
@click.pass_context
def setup_db(ctx):
    """Sets up user roles and adds an admin account."""
    ctx.invoke(create_admin)
    for role in ["student", "company"]:
        ctx.invoke(create_role, name=role)
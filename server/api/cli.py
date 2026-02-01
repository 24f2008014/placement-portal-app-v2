import click
from flask import Blueprint
from api import db
from api.models import User, Role, Department, Branch

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

@bp.cli.command('create-department')
@click.argument('name')
def create_department(name):
    """Adds the specified department to the `Department` table."""
    department = db.session.execute(db.select(Department).where(Department.name == name)).scalar_one_or_none()
    if department is None:
        department = Department(name=name)
        db.session.add(department)
        click.echo(f"'{name}' department added to 'Department' table.")
        db.session.commit()
    else:
        click.echo(f"'{name}' department already exists in 'Department' table.")

@bp.cli.command('create-branch')
@click.argument('branch_name')
@click.argument('department_name')
def create_branch(branch_name, department_name):
    """Adds the specified branch to the `Branch` table."""
    branch = db.session.execute(db.select(Branch).where(Branch.name == branch_name)).scalar_one_or_none()
    if branch is None:
        department = db.session.execute(db.select(Department).where(Department.name == department_name)).scalar_one_or_none()
        branch = Branch(name=branch_name, department_id=department.id)
        db.session.add(branch)
        click.echo(f"'{branch_name}' branch added to 'Branch' table.")
        db.session.commit()
    else:
        click.echo(f"'{branch_name}' branch already exists in 'Branch' table.")

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
    """Sets up user roles and departments and adds an admin account."""
    ctx.invoke(create_admin)
    for role in ["student", "company"]:
        ctx.invoke(create_role, name=role)
    for department in ["Computer Science and Engineering", "Data Science and Artificial Intelligence", "Electrical Engineering"]:
        ctx.invoke(create_department, name=department)
    for branch in ["B.S. in Computational Biology", "B.S. in Computer Science", "B.S. in Human-Computer Interaction"]:
        ctx.invoke(create_branch, branch_name=branch, department_name="Computer Science and Engineering")
    for branch in ["B.S. in Data Analysis", "B.S. in Machine Learning"]:
        ctx.invoke(create_branch, branch_name=branch, department_name="Data Science and Artificial Intelligence")
    for branch in ["B.S. in Electrical Engineering"]:
        ctx.invoke(create_branch, branch_name=branch, department_name="Electrical Engineering")
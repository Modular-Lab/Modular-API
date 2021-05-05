# coding: utf-8
import sys
import os
import venv
import shutil
import subprocess
import time
import json
import re
import traceback
from pathlib import Path
from typing import Any, List, Optional
# from importlib import import_module
from contextlib import redirect_stdout

import click
import git

from alembic import command


import typer

from modularapi.utils import AlembicConfig, _on_rmtree_error


if sys.version_info < (3, 6, 1):
    typer.echo("This framework need at least Python 3.6.1")
    exit(code=1)


cli = typer.Typer()


def result_callback(result: Any) -> None:
    ctx = click.get_current_context()
    typer.echo(
        f"{ctx.obj['style']['success']} in {time.time() - ctx.obj['start_time']:.3f}s.",
        err=True,
    )


@cli.callback(result_callback=result_callback)
def setup(
    ctx: typer.Context,
):
    ctx.ensure_object(dict)
    ctx.obj = {
        "start_time": time.time(),
        "style": {
            "info": typer.style(
                "INFO", bg=typer.colors.WHITE, fg=typer.colors.BLACK, bold=True
            ),
            "success": typer.style(
                "SUCCESS", bg=typer.colors.GREEN, fg=typer.colors.BLACK, bold=True
            ),
            "warning": typer.style(
                "WARNING", bg=typer.colors.YELLOW, fg=typer.colors.BLACK, bold=True
            ),
            "error": typer.style(
                "ERROR", bg=typer.colors.RED, fg=typer.colors.BLACK, bold=True
            ),
        },
    }


@cli.command(name="version")
def cli_version(
    ctx: typer.Context,
):
    """
    Check the version of Modular-API.
    """
    import modularapi

    typer.echo(
        f"{ctx.obj['style']['info']} Modular-API is installed : version {modularapi.__version__}",
        err=True,
    )


# db
cli_db = typer.Typer(
    name="db",
    help="Manage your PostgreSQL database.",
    short_help="Manage your PostgreSQL database.",
)
cli.add_typer(cli_db)


# db branches
@cli_db.command(name="branches")
def cli_db_branches(
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Output in verbose mode",
    )
):
    """
    Show current branch points.
    """
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("script_location", str(Path() / "db_migrations"))
    command.branches(config=alembic_cfg, verbose=verbose)


# db current
@cli_db.command(name="current")
def cli_db_current(
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Output in verbose mode",
    )
):
    """
    Display the current revision for a database.
    """
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("script_location", str(Path() / "db_migrations"))
    command.current(config=alembic_cfg, verbose=verbose)


# db downgrade <revision>
@cli_db.command(name="downgrade")
def cli_db_downgrade(
    revision: str = typer.Argument(
        ...,
        help="A string revision target or range for –sql mode",
    ),
    sql: bool = typer.Option(
        False,
        help="Use the SQL mode",
    ),
):
    """
    Revert to a previous version.
    """
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("script_location", str(Path() / "db_migrations"))
    command.downgrade(config=alembic_cfg, revision=revision, sql=sql)


# db edit <rev>
@cli_db.command(name="edit")
def cli_db_edit(
    rev: str = typer.Argument(
        ...,
        help="A string revision target",
    )
):
    """
    Edit revision script(s) using $EDITOR.
    """
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("script_location", str(Path() / "db_migrations"))
    command.edit(config=alembic_cfg, rev=rev)


# db heads
@cli_db.command(name="heads")
def cli_db_heads(
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Output in verbose mode",
    ),
    resolve_dependencies: bool = typer.Option(
        False,
        "--resolve-dependencies",
        help="Treat dependency version as down revisions.",
    ),
):
    """
    Revert to a previous version.
    """
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("script_location", str(Path() / "db_migrations"))
    command.heads(
        config=alembic_cfg,
        verbose=verbose,
        resolve_dependencies=resolve_dependencies,
    )


# db history
@cli_db.command(name="history")
def cli_db_history(
    rev_range: bool = typer.Option(
        False,
        "--rev-range",
        help="String revision range.",
    ),
    verbose: bool = typer.Option(
        False,
        "-v",
        "--verbose",
        help="Output in verbose mode.",
    ),
    indicate_current: bool = typer.Option(
        False,
        "--indicate_current",
        help="Indicate current revision.",
    ),
):
    """
    List changeset scripts in chronological order.
    """
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("script_location", str(Path() / "db_migrations"))
    command.history(
        config=alembic_cfg,
        rev_range=rev_range,
        verbose=verbose,
        indicate_current=indicate_current,
    )


# db merge
@cli_db.command(name="merge")
def cli_db_merge(
    revisions: List[str] = typer.Argument(
        ...,
        help="You can pass to it an argument such as heads, meaning we’d like to merge all heads."
        " Or, you can pass it individual revision numbers sequentally:",
    ),
    message: Optional[str] = typer.Option(
        None,
        "-m",
        "--message",
        help="A string message to apply to the revision",
    ),
    branche_label: Optional[str] = typer.Option(
        None,
        "--branch-label",
        help="A string label name to apply to the new revision",
    ),
    rev_id: Optional[str] = typer.Option(
        None,
        "--rev-id",
        help="Hardcoded revision identifier instead of generating a new one.",
    ),
):
    """
    Merge two (or more) revisions together. Creates a new migration file.
    """
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("script_location", str(Path() / "db_migrations"))
    command.merge(
        config=alembic_cfg,
        revisions=revisions,
        message=message,
        branch_label=branche_label,
        rev_id=rev_id,
    )


# db revision
@cli_db.command(name="revision")
def cli_db_revision(
    message: Optional[str] = typer.Option(
        None,
        "-m",
        "--message",
        help="A message to apply to the revision.",
    ),
    autogenerate: bool = typer.Option(
        False,
        "-autogenerate",
        help="Whether or not to autogenerate the script from the database.",
    ),
    sql: bool = typer.Option(
        False,
        "-sql",
        help="Whether to dump the script out as a SQL string; when specified, the script is dumped to stdout.",
    ),
    head: str = typer.Option(
        "head",
        "--head",
        help="Head revision to build the new revision upon as a parent.",
    ),
    splice: bool = typer.Option(
        False,
        "--splice",
        help="Whether or not the new revision should be made into a new head of its own;"
        " is required when the given head is not itself a head.",
    ),
    branch_label: Optional[str] = typer.Option(
        None,
        "--branche-label",
        help="A string label to apply to the branch.",
    ),
    version_path: Optional[str] = typer.Option(
        None,
        "--version-path",
        help="String symbol identifying a specific version path from the configuration.",
    ),
    rev_id: Optional[str] = typer.Option(
        None,
        "--rev-id",
        help="Optional revision identifier to use instead of having one generated.",
    ),
):
    """
    Create a new revision file.
    """
    from modularapi.settings import get_setting

    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", get_setting().PG_DNS)
    alembic_cfg.set_main_option("script_location", str(Path() / "db_migrations"))
    command.revision(
        config=alembic_cfg,
        message=message,
        autogenerate=autogenerate,
        sql=sql,
        head=head,
        splice=splice,
        branch_label=branch_label,
        version_path=version_path,
        rev_id=rev_id,
    )


# db show <rev>
@cli_db.command(name="show")
def cli_db_show(
    revisions: str = typer.Argument(
        ...,
        help="A string revision target.",
    ),
):
    """
    Show the revision(s) denoted by the given symbol.
    """
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("script_location", str(Path() / "db_migrations"))
    command.show(config=alembic_cfg, rev=revisions)


# db stamp <revision='head'>
@cli_db.command(name="stamp")
def cli_db_stamp(
    revisions: List[str] = typer.Argument(
        ...,
        help="target revision or list of revisions. May be a list to indicate stamping of multiple branch heads.",
    ),
    sql: bool = typer.Option(
        False,
        "--sql",
        help="Use the SQL mode.",
    ),
    purge: bool = typer.Option(
        False,
        "--purge",
        help="Delete all entries in the version table before stamping.",
    ),
):
    """
    Stamp the revision table with the given revision; don’t run any migrations.
    """
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("script_location", str(Path() / "db_migrations"))
    command.stamp(config=alembic_cfg, revision=revisions, sql=sql, purge=purge)


# db upgrade <revision>
@cli_db.command(name="upgrade")
def cli_db_upgrade(
    revision: str = typer.Argument(
        ...,
        help="A string revision target or range for –sql mode",
    ),
    sql: bool = typer.Option(
        False,
        "--sql",
        help="Use the SQL mode.",
    ),
):
    """
    Upgrade to a later version.
    """
    alembic_cfg = AlembicConfig("alembic.ini")
    alembic_cfg.set_main_option("script_location", str(Path() / "db_migrations"))
    command.upgrade(config=alembic_cfg, revision=revision, sql=sql)


# module
cli_modules = typer.Typer(
    name="modules",
    help="Manage your modules.",
    short_help="Manage your modules.",
)
cli.add_typer(cli_modules)


# modules add <git_remote_link>
@cli_modules.command(name="add")
def cli_modules_add(
    ctx: typer.Context,
    github_repo: str = typer.Argument(
        ...,
        help="The git remote URL",
    ),
):
    """
    Add a module from a git remote url ( github / gitlab / ect... ).
    """
    p = Path("./modules")

    if not p.is_dir():
        typer.echo(
            f"{ctx.obj['style']['warning']} The `modules` directory doesn't exist, creating one ..."
        )
    p.mkdir(parents=True, exist_ok=True)

    m = re.match(r"https?://(.+\..+)/(?P<owner>.+)/(?P<name>.+)(\.git)?", github_repo)
    if m:
        repo_name = f"{m.group('owner')}_{m.group('name')}"
    else:
        # fallback name
        if github_repo.endswith(".git"):
            repo_name = github_repo.split("/")[-1].split(".")[:-1]
        else:
            repo_name = github_repo.split("/")[-1]

    if (p / repo_name).is_dir():
        typer.echo(
            f"{ctx.obj['style']['error']} The module `{repo_name}` is already installed !"
        )
        raise typer.Exit(code=1)

    typer.echo(f"{ctx.obj['style']['info']} Downloading the module ...")

    try:
        git.Repo.clone_from(url=github_repo, to_path=p / repo_name)
    except git.exc.CommandError:
        typer.echo(
            f"{ctx.obj['style']['error']} Repository `{github_repo}` doesn't exist !"
        )
        raise typer.Exit(code=1)

    typer.echo(
        f"{ctx.obj['style']['success']} The module has been installed in `{p / repo_name}`."
    )
    typer.echo(
        f"{ctx.obj['style']['info']} Searching for a `requirements.txt` file ..."
    )
    req_file = p / repo_name / "requirements.txt"
    if req_file.is_file():
        typer.echo(
            f"{ctx.obj['style']['info']} requirements file found, installing dependencies on the venv ..."
        )

        # on Windows
        if os.name == "nt":
            python_path = Path("venv") / "Scripts" / "python.exe"

        # on Unix
        else:
            python_path = Path("venv") / "bin" / "python"

        subprocess.run(
            [python_path, "-m", "pip", "install", "-r", req_file, "--upgrade"],
            check=True,
        )
    else:
        typer.echo(f"{ctx.obj['style']['info']} requirements files not found.")


# modules remove <module_name>
@cli_modules.command(name="remove")
def cli_modules_remove(
    ctx: typer.Context,
    module_name: str = typer.Argument(
        ...,
        help="The module name to remove",
    ),
):
    """
    Remove a module.
    """
    p = Path("./modules") / Path(module_name)
    if not p.is_dir():
        typer.echo(
            f"{ctx.obj['style']['error']} The module `{module_name}` doesn't exist !"
        )
        raise typer.Exit(code=1)

    typer.echo(f"{ctx.obj['style']['info']} Uninstalling `{module_name}` ...")
    shutil.rmtree(p, onerror=_on_rmtree_error)
    typer.echo(
        f"{ctx.obj['style']['success']} `{module_name}` has been correctly removed."
    )


# modules purge
@cli_modules.command(name="purge")
def cli_modules_purge(
    ctx: typer.Context,
):
    """
    Remove all modules.
    """
    p = Path("./modules")
    if not p.is_dir():
        typer.echo(f"{ctx.obj['style']['error']} There is no modules directory !")
        raise typer.exit(code=1)

    shutil.rmtree(p, onerror=_on_rmtree_error)
    p.mkdir(parents=True, exist_ok=True)


# modules update <module_name>
@cli_modules.command(name="update")
def cli_modules_update(
    ctx: typer.Context,
    module_name: str = typer.Argument(
        ...,
        help="The module name to update",
    ),
):
    """
    Update a module from a git remote.
    """
    p = Path("./modules") / module_name

    if not p.is_dir():
        typer.echo(
            f"{ctx.obj['style']['error']} The module `{module_name}` doesn't exist"
        )
        raise typer.Exit(code=1)

    typer.echo(f"{ctx.obj['style']['info']} Updating `{module_name}` ...")

    try:
        repo = git.Repo(p)
    except git.exc.InvalidGitRepositoryError:
        typer.echo(
            f"{ctx.obj['style']['error']} the module `{p}` isn't valid (probably missing the .git folder) !",
        )
        raise typer.Exit(code=1)

    try:
        repo.remotes.origin.pull()
    except git.exc.GitCommandError:
        # In the case the repo was deleted from github/gitlab/ect
        typer.echo(
            f"{ctx.obj['style']['error']} Unable to update, check the remote origin !"
        )
        raise typer.Exit(code=1)

    typer.echo(f"{ctx.obj['style']['info']} `{module_name}` has been updated.")
    typer.echo(
        f"{ctx.obj['style']['info']} Searching for a `requirements.txt` file ..."
    )

    req_file = p / "requirements.txt"
    if req_file.is_file():
        typer.echo(
            f"{ctx.obj['style']['info']} requirements file found, installing dependencies on the venv ..."
        )

        # on Windows
        if os.name == "nt":
            python_path = Path("venv") / "Scripts" / "python.exe"

        # on Unix
        else:
            python_path = Path("venv") / "bin" / "python"

        subprocess.run(
            [python_path, "-m", "pip", "install", "-r", req_file, "--upgrade"],
            check=True,
        )
    else:
        typer.echo(f"{ctx.obj['style']['info']} requirements files not found.")


# modules update-all
@cli_modules.command(name="update-all")
def cli_modules_update_all(
    ctx: typer.Context,
):
    """
    Update all modules.
    """
    p = Path("./modules")
    for module_name in p.glob("*"):
        if module_name.is_dir():
            try:
                repo = git.Repo(p / module_name)
                repo.remotes.origin.pull()
            except git.exc.InvalidGitRepositoryError:
                typer.echo(
                    f"{ctx.obj['style']['warning']} the module `{module_name}` couldn't be updated !",
                )
            except git.exc.GitCommandError:
                # In the case the repo was deleted from github/gitlab/ect
                typer.echo(
                    f"{ctx.obj['style']['error']} Unable to update, check the remote origin !"
                )
            typer.echo(
                f"{ctx.obj['style']['info']} Searching for a `requirements.txt` file ..."
            )

            req_file = module_name / "requirements.txt"
            if req_file.is_file():
                typer.echo(
                    f"{ctx.obj['style']['info']} requirements file found, installing dependencies on the venv ..."
                )

                # on Windows
                if os.name == "nt":
                    python_path = Path("venv") / "Scripts" / "python.exe"

                # on Unix
                else:
                    python_path = Path("venv") / "bin" / "python"

                subprocess.run(
                    [python_path, "-m", "pip", "install", "-r", req_file, "--upgrade"],
                    check=True,
                )
            else:
                typer.echo(f"{ctx.obj['style']['info']} requirements files not found.")


# modules export <file.json=sys.stdout>
@cli_modules.command(name="export")
def cli_modules_export(
    ctx: typer.Context,
    output_file: typer.FileTextWrite = typer.Argument(
        sys.stdout,
        help="The output file (sys.stdout by default).",
    ),
):
    """
    Export all modules as json format.
    """
    repos = {}
    for module_name in Path("./modules").glob("*"):
        if module_name.is_dir():
            try:
                repos[module_name.parts[-1]] = git.Repo(module_name)
            except git.exc.InvalidGitRepositoryError:
                typer.echo(
                    f"{ctx.obj['style']['warning']} the module `{module_name}` couldn't be exported !"
                )

    res = {str(path): list(repo.remotes.origin.urls) for path, repo in repos.items()}
    json.dump(res, fp=output_file, indent=4, sort_keys=True)
    if output_file is sys.stdout:
        sys.stdout.flush()


# modules import <file.json=sys.stdin>
@cli_modules.command(name="import")
def cli_modules_import(
    ctx: typer.Context,
    input_file: typer.FileText = typer.Argument(
        sys.stdin,
        help="The input file (sys.stdin by default).",
    ),
):
    """
    Import all modules from json format file.
    """
    p = Path("./modules")
    for module, repo_urls in json.load(fp=input_file).items():
        try:
            git.Repo.clone_from(url=repo_urls[0], to_path=(p / module))
        except (IndexError, git.exc.GitCommandError):
            typer.echo(
                f"{ctx.obj['style']['warning']} the module `{module}` couldn't be imported !"
            )


# modules update list
@cli_modules.command(name="list")
def cli_modules_list(
    ctx: typer.Context,
):
    """
    List all installed modules.
    """
    p = Path("modules")
    if not p.is_dir():
        typer.echo(
            f"{ctx.obj['style']['error']} There is no modules directory !", err=True
        )
        raise typer.Exit(code=1)

    modules = [m.parts[-1] for m in p.glob("*") if m.is_dir()]
    if modules:
        typer.echo("\n".join(f"{m} is installed" for m in modules))
    else:
        typer.echo(f"{ctx.obj['style']['warning']} There is no module installed !")


# modules create <module_name>
@cli_modules.command(name="create")
def cli_modules_create(
    ctx: typer.Context,
    module_name: str = typer.Argument(..., help="The module name to create."),
    readme: bool = typer.Option(
        False,
        "--readme",
        "--with-readmy",
        help="Keep the readme.md file in your module.",
    ),
):
    """
    Create a module from the official template
    """
    template_url = "https://github.com/Modular-Lab/module_template.git"

    p = Path("modules")

    # ensure the modules directory exists
    p.mkdir(exist_ok=True)

    if (p / module_name).is_dir():
        typer.echo(f"{ctx.obj['style']['error']} The module already exists !", err=True)
        raise typer.Exit(code=1)

    try:
        git.Repo.clone_from(url=template_url, to_path=p / module_name)
    except git.exc.CommandError:
        typer.echo(
            f"{ctx.obj['style']['error']} Unable to clone the template !", err=True
        )
        typer.echo(traceback.format_exc())
        raise typer.Exit(code=1)

    shutil.rmtree(p / module_name / ".git", onerror=_on_rmtree_error)
    (p / module_name / "LICENSE").unlink(missing_ok=True)

    if not readme:
        (p / module_name / "readme.md").unlink(missing_ok=True)

    typer.echo(
        f"{ctx.obj['style']['success']} The module has been created in `{p / module_name}`."
    )


# init <project_name>
@cli.command(name="init")
def cli_projet_init(
    ctx: typer.Context,
    project_path: Path = typer.Argument(
        ...,
        dir_okay=True,
        writable=True,
        help="The project name",
    ),
):
    """
    Init a new Modular project
    """
    # check if the path already exists
    if project_path.is_dir():
        typer.echo(f"{ctx.obj['style']['error']} the path `{project_path}` already exists !")
        raise typer.Exit(code=1)

    # Initialization
    typer.echo(
        f"{ctx.obj['style']['info']} Initializing a new project at `{project_path}` ..."
    )
    (project_path / "modules").mkdir(parents=True)

    alembic_cfg = AlembicConfig(file_=project_path / "alembic.ini")
    alembic_cfg.set_main_option("script_location", str(project_path / "db_migrations"))

    # initialize the db migrations
    with open(os.devnull, "w") as f:
        with redirect_stdout(f):
            command.init(
                config=alembic_cfg,
                directory=project_path / "db_migrations",
                template="default",
            )

    # creating the venv
    typer.echo(f"{ctx.obj['style']['info']} Creating the venv ...")
    venv.EnvBuilder(with_pip=True).create(project_path / "venv")

    # install dependancies
    typer.echo(f"{ctx.obj['style']['info']} Installing dependancies in the venv ...")

    # on Windows
    if os.name == "nt":
        python_path = project_path / "venv" / "Scripts" / "python.exe"

    # on Unix
    else:
        python_path = project_path / "venv" / "bin" / "python"

    subprocess.run([python_path, "-m", "pip", "install", "-U", "pip"], check=True)
    subprocess.run(
        [
            python_path,
            "-m",
            "pip",
            "install",
            "-r",
            Path(__file__).parent / "venv_requirements.txt",
        ],
        check=True,
    )

    shutil.copyfile(
        src=Path(__file__).parent / "venv_requirements.txt",
        dst=project_path / "requirements.txt",
    )

    with open(project_path / ".env", "w", encoding="utf-8") as f:
        print('ENVIRONMENT="developpment"', file=f)
        print('PG_DNS="postgres://user:password@host:port/database"', file=f)

    cd_message = typer.style(f"cd {project_path}", bold=True, fg="green")
    modularAPI_message = typer.style("ModularAPI", bold=True, fg="green")
    typer.echo(
        f"\n{ctx.obj['style']['success']} You can now do `{cd_message}` and start using {modularAPI_message}"
    )
    typer.echo(f"\nDon't forget to edit `{project_path / '.env'}` !")


if __name__ == "__main__":
    cli()

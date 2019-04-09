import pathlib
import re
import shutil
import subprocess

import invoke
import parver
from towncrier._builder import find_fragments, render_fragments, split_fragments
from towncrier._settings import load_config


def _get_git_root(ctx):
    return pathlib.Path(
        ctx.run("git rev-parse --show-toplevel", hide=True).stdout.strip()
    )


ROOT = pathlib.Path(__file__).resolve().parent.parent

PACKAGE_NAME = "vistir"

INIT_PY = ROOT.joinpath("src", PACKAGE_NAME, "__init__.py")


@invoke.task()
def clean(ctx):
    """Clean previously built package artifacts.
    """
    ctx.run(f"python setup.py clean")
    dist = ROOT.joinpath("dist")
    print(f"[clean] Removing {dist}")
    if dist.exists():
        shutil.rmtree(str(dist))


def _read_version():
    out = subprocess.check_output(["git", "tag"], encoding="ascii")
    try:
        version = max(
            parver.Version.parse(v).normalize()
            for v in (line.strip() for line in out.split("\n"))
            if v
        )
    except ValueError:
        version = parver.Version.parse("0.0.0")
    return version


def _write_version(v):
    lines = []
    with INIT_PY.open() as f:
        for line in f:
            if line.startswith("__version__ = "):
                line = f"__version__ = {repr(str(v))}\n".replace("'", '"')
            lines.append(line)
    with INIT_PY.open("w", newline="\n") as f:
        f.write("".join(lines))


def _render_log():
    """Totally tap into Towncrier internals to get an in-memory result.
    """
    config = load_config(ROOT)
    definitions = config["types"]
    fragments, fragment_filenames = find_fragments(
        pathlib.Path(config["directory"]).absolute(),
        config["sections"],
        None,
        definitions,
    )
    rendered = render_fragments(
        pathlib.Path(config["template"]).read_text(encoding="utf-8"),
        config["issue_format"],
        split_fragments(fragments, definitions),
        definitions,
        config["underlines"][1:],
        False,  # Don't add newlines to wrapped text.
    )
    return rendered


REL_TYPES = ("major", "minor", "patch")


def _bump_release(version, type_, log=False):
    if type_ not in REL_TYPES:
        raise ValueError(f"{type_} not in {REL_TYPES}")
    index = REL_TYPES.index(type_)
    next_version = version.base_version().bump_release(index=index)
    if log:
        print(f"[bump] {version} -> {next_version}")
    print(f"{next_version}")
    return next_version


def _prebump(version, prebump, log=False):
    next_version = version.bump_release(index=prebump).bump_dev()
    if log:
        print(f"[bump] {version} -> {next_version}")
    print(f"{next_version}")
    return next_version


PREBUMP = "patch"


@invoke.task(pre=[clean])
def build(ctx):
    ctx.run("python setup.py sdist bdist_wheel")


@invoke.task()
def get_next_version(ctx, type_="patch", log=False):
    version = _read_version()
    if type_ in ("dev", "pre"):
        idx = REL_TYPES.index("patch")
        new_version = _prebump(version, idx, log=log)
    else:
        new_version = _bump_release(version, type_, log=log)
    return new_version


@invoke.task()
def bump_version(ctx, type_="patch", log=False):
    new_version = get_next_version(ctx, type_, log=log)
    _write_version(new_version)
    return new_version


@invoke.task()
def generate_news(ctx, yes=False):
    command = "towncrier"
    if yes:
        command = f"{command} --yes"
    ctx.run(command)


@invoke.task()
def get_changelog(ctx):
    changelog = _render_log()
    print(changelog)
    return changelog


@invoke.task(optional=["version", "type_"])
def tag_release(ctx, version=None, type_="patch", yes=False):
    if version is None:
        version = bump_version(ctx, type_)
    else:
        _write_version(version)
    tag_content = get_changelog(ctx)
    generate_news(ctx, yes=yes)
    ctx.run(f'git commit -am "Release {version}"')
    tag_content = tag_content.replace('"', '\\"')
    ctx.run(f'git tag -a {version} -m "Version {version}\n\n{tag_content}"')


@invoke.task(pre=[clean])
def release(ctx, type_, repo, prebump=PREBUMP, yes=False):
    """Make a new release.
    """
    if prebump not in REL_TYPES:
        raise ValueError(f"{type_} not in {REL_TYPES}")
    prebump = REL_TYPES.index(prebump)

    version = bump_version(ctx, type_, log=True)

    # Needs to happen before Towncrier deletes fragment files.

    tag_release(version, yes=yes)

    ctx.run(f"python setup.py sdist bdist_wheel")

    dist_pattern = f'{PACKAGE_NAME.replace("-", "[-_]")}-*'
    artifacts = list(ROOT.joinpath("dist").glob(dist_pattern))
    filename_display = "\n".join(f"  {a}" for a in artifacts)
    print(f"[release] Will upload:\n{filename_display}")
    if not yes:
        try:
            input("[release] Release ready. ENTER to upload, CTRL-C to abort: ")
        except KeyboardInterrupt:
            print("\nAborted!")
            return

    arg_display = " ".join(f'"{n}"' for n in artifacts)
    ctx.run(f'twine upload --repository="{repo}" {arg_display}')

    version = _prebump(version, prebump)
    _write_version(version)

    ctx.run(f'git commit -am "Prebump to {version}"')


@invoke.task
def build_docs(ctx):
    from vistir import __version__

    _current_version = parver.Version.parse(__version__)
    minor = [str(i) for i in _current_version.release[:2]]
    docs_folder = (_get_git_root(ctx) / "docs").as_posix()
    if not docs_folder.endswith("/"):
        docs_folder = "{0}/".format(docs_folder)
    args = ["--ext-autodoc", "--ext-viewcode", "-o", docs_folder]
    args.extend(["-A", "'Dan Ryan <dan@danryan.co>'"])
    args.extend(["-R", str(_current_version)])

    args.extend(["-V", ".".join(minor)])
    args.extend(["-e", "-M", "-F", f"src/{PACKAGE_NAME}"])
    print("Building docs...")
    ctx.run("sphinx-apidoc {0}".format(" ".join(args)))


@invoke.task
def clean_mdchangelog(ctx):
    root = _get_git_root(ctx)
    changelog = root / "CHANGELOG.md"
    content = changelog.read_text()
    content = re.sub(
        r"([^\n]+)\n?\s+\[[\\]+(#\d+)\]\(https://github\.com/sarugaku/[\w\-]+/issues/\d+\)",
        r"\1 \2",
        content,
        flags=re.MULTILINE,
    )
    changelog.write_text(content)

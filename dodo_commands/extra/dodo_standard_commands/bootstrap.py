"""Pull the latest version of the Dodo Commands system."""
import glob
import os
import sys
from argparse import ArgumentParser

from dodo_commands import CommandError, Dodo
from dodo_commands.framework.config_io import ConfigIO
from dodo_commands.framework.paths import Paths
from dodo_commands.framework.util import query_yes_no, symlink


def _args():
    parser = ArgumentParser()
    parser.add_argument(
        "src_dir", help="The src directory for the bootstrapped project"
    )
    parser.add_argument(
        "shared_config_dir",
        help="Location relative to src_dir where the shared project config is stored",
    )
    parser.add_argument("--force", dest="use_force", action="store_true")

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--git-url",
        dest="git_url",
        help="Clone this repository to the src_dir location",
    )
    group.add_argument(
        "--link-dir",
        help="Make the src directory a symlink to this directory",
    )
    group.add_argument(
        "--cookiecutter-url",
        help="Use cookiecutter to create the src_dir location",
    )

    parser.add_argument(
        "--depth", type=int, default=0, help="Depth for cloning repositories"
    )
    parser.add_argument("--branch", help="Branch to checkout after cloning")

    parser.add_argument(
        "--src-subdir",
        help="Specify a subdirectory of src_dir to clone into",
    )

    args = Dodo.parse_args(parser)
    args.project_dir = Dodo.get("/ROOT/project_dir")
    return args


def _report(msg):
    sys.stderr.write(msg + "\n")


def _copy_defaults(args, shared_config_dir):
    config_dir = os.path.join(args.project_dir, ".dodo_commands")
    for filename in glob.glob(os.path.join(shared_config_dir, "*")):
        dest_path = os.path.join(config_dir, os.path.basename(filename))
        if os.path.exists(dest_path):
            if args.confirm:
                print(
                    "Warning, destination path already exists: %s. Overwrite it?"
                    % dest_path
                )
            elif args.use_force:
                print("Overwriting existing path: %s" % dest_path)
            else:
                raise CommandError(
                    "Destination path %s already exists. " % dest_path
                    + "Use the --confirm or --force flag to overwrite it."
                )
        Dodo.run(["cp", "-rf", filename, dest_path])


def _clone(args, src_dir):
    if os.path.exists(src_dir):
        raise CommandError("Cannot clone into %s, path already exists" % src_dir)

    Dodo.run(
        ["git", "clone", args.git_url, os.path.basename(src_dir)]
        + (["--depth", args.depth] if args.depth else []),
        cwd=os.path.dirname(src_dir),
    )
    if args.branch:
        Dodo.run(["git", "checkout", args.branch], cwd=src_dir)


def _cookiecutter(src_dir, cookiecutter_url):
    if os.path.exists(src_dir):
        raise CommandError("Cannot clone into %s, path already exists" % src_dir)

    Dodo.run(["cookiecutter", cookiecutter_url, "-o", src_dir])


def _link_dir(link_target, link_name):
    if os.path.exists(link_name):
        raise CommandError("Cannot create a link because %s already exists" % link_name)
    if os.name == "nt" and not args.confirm:
        symlink(link_target, link_name)
    else:
        Dodo.run(["ln", "-s", link_target, link_name])


def _get_full_src_dir(src_dir, src_subdir):
    postfix = os.path.join(src_dir, src_subdir) if src_subdir else src_dir
    return (
        postfix
        if os.path.isabs(src_dir)
        else os.path.abspath(os.path.join(args.project_dir, postfix))
    )


if Dodo.is_main(__name__, safe=True):
    args = _args()

    full_src_dir = _get_full_src_dir(args.src_dir, args.src_subdir)
    Dodo.run(["mkdir", "-p", os.path.dirname(full_src_dir)])

    if args.git_url:
        _clone(args, full_src_dir)
    elif args.link_dir:
        _link_dir(os.path.expanduser(args.link_dir), full_src_dir)
    elif args.cookiecutter_url:
        _cookiecutter(full_src_dir, os.path.expanduser(args.cookiecutter_url))

    shared_config_dir = os.path.join(full_src_dir, args.shared_config_dir)
    _copy_defaults(args, shared_config_dir)

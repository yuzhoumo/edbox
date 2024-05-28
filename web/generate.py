import jinja2
import minify_html
import pathlib
import json
import shutil
import os

from typing import TypedDict
from edapi.types.api_types.course import API_Course
from edapi.types.api_types.thread import API_Thread_WithComments, API_Thread_Comment, API_User_Short


AVATARS_DIR = "avatars/"
FILES_DIR = "files/"
INFO_FILE = "info.json"
USERS_FILE = "users.json"
POSTS_FILE = "posts.json"
EXPECTED_PATHS = [AVATARS_DIR, FILES_DIR, INFO_FILE, USERS_FILE, POSTS_FILE]


class CourseArchive(TypedDict):
    base_dir: pathlib.Path
    info: API_Course
    posts: list[API_Thread_WithComments]
    users: list[API_User_Short]


def validate_archive_dir(base_dir: str):
    """Ensure the expected archive files/directories exist"""
    if not os.path.isdir(base_dir):
        raise FileNotFoundError(f"Invalid base directory: {base_dir}")
    for e in EXPECTED_PATHS:
        path = f"{base_dir}/{e}"
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path not found: {path}")


def read_course_archive(base_dir: str) -> CourseArchive:
    """Deserialize course data from archived files"""
    validate_archive_dir(base_dir)
    with open(f"{base_dir}/{INFO_FILE}", "r") as f:
        info: API_Course = json.loads(f.read())
    with open(f"{base_dir}/{USERS_FILE}", "r") as f:
        users: list[API_User_Short] = json.loads(f.read())
    with open(f"{base_dir}/{POSTS_FILE}", "r") as f:
        posts: list[API_Thread_WithComments] = json.loads(f.read())
    return {
        "base_dir": pathlib.Path(base_dir),
        "info": info,
        "posts": posts,
        "users": users,
    }


def transform_documents_to_html(posts: list[API_Thread_WithComments]) -> list[API_Thread_WithComments]:
    """Transform the Ed's adhoc 'document' XML format into regular HTML"""
    # TODO
    return posts


def copy_and_overwrite(from_path, to_path):
    """Recursively copy and overwrite directory"""
    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)


def generate_site(src_dir: str, target_dir: str):
    """Generate static site from archived data"""
    archive = read_course_archive(src_dir)
    archive["posts"] = transform_documents_to_html(archive["posts"])

    dir_path = os.path.dirname(os.path.realpath(__file__))
    templateLoader = jinja2.FileSystemLoader(searchpath=f"{dir_path}/templates")
    templateEnv = jinja2.Environment(loader=templateLoader)

    sidebar = templateEnv.get_template("sidebar.jinja")
    main = templateEnv.get_template("main.jinja")
    index = templateEnv.get_template("index.jinja")

    index_out = index.render({
        "posts": json.dumps(archive["posts"]),
        "users": json.dumps(archive["users"]),
        "sidebar_content": sidebar.render(),
        "main_content": main.render(),
    })

    minified = minify_html.minify(
        index_out,
        minify_css=True,
        remove_processing_instructions=True
    )

    with open(f"{target_dir}/index.html", "w") as f:
        f.write(minified)

    copy_and_overwrite(f"{dir_path}/static", f"{target_dir}/static")


if __name__ == "__main__":
    generate_site("assets", "./")


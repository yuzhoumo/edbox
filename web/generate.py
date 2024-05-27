import pathlib
import json
import os

from typing import TypedDict
from edapi.types.api_types.course import API_Course
from edapi.types.api_types.thread import API_Thread_WithComments, API_User_Short


AVATARS_DIR    = "avatars/"
FILES_DIR      = "files/"
INFO_FILE      = "info.json"
USERS_FILE     = "users.json"
POSTS_FILE     = "posts.json"
EXPECTED_PATHS = [ AVATARS_DIR, FILES_DIR, INFO_FILE, USERS_FILE, POSTS_FILE ]


class CourseArchive(TypedDict):
    base_dir: pathlib.Path
    info: API_Course
    posts: list[API_Thread_WithComments]
    users: list[API_User_Short]


def validate_archive_dir(base_dir: str):
    if not os.path.isdir(base_dir):
        raise FileNotFoundError(f"Invalid base directory: {base_dir}")
    for e in EXPECTED_PATHS:
        path = f"{base_dir}/{e}"
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path not found: {path}")


def read_course_archive(base_dir: str) -> CourseArchive:
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


def generate_site(src_dir: str, target_dir: str):
    archive = read_course_archive(src_dir)
    print(archive)


if __name__ == "__main__":
    archive = read_course_archive("test")
    print(archive["posts"])

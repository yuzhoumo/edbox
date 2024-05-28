import jinja2
import minify_html
import pathlib
import json
import shutil
import os
import re

from typing import TypedDict
from edapi.types.api_types.course import API_Course
from edapi.types.api_types.thread import API_Thread_Comment, API_Thread_WithComments, API_User_Short
from edapi.types.api_types.content import ContentString


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


def transform_documents_to_html(posts):
    """Transform the Ed's adhoc 'document' XML format into regular HTML"""
    if len(posts) == 0:
        return []

    SIMPLE_TRANSFORMATIONS = {
        "paragraph": "p",
        "link": "a",
        "bold": "b",
        "italic": "i",
        "underline": "ins",
        "strike": "del",
    }

    def simple_transform(text, old_tag, new_tag):
        pattern = rf'<{old_tag}(.*?)>(.*?)</{old_tag}>'
        def replace_with_new_tag(match):
            attributes = match.group(1)
            inner_text = match.group(2)
            return f'<{new_tag}{attributes}>{inner_text}</{new_tag}>'
        replaced_text = re.sub(pattern, replace_with_new_tag, text)
        return replaced_text

    for i, post in enumerate(posts):
        content = post["content"]
        for k, v in SIMPLE_TRANSFORMATIONS.items():
            content = ContentString(simple_transform(content, k, v))
        posts[i]["content"] = content

        if "answers" in post:
            answers = post["answers"]
            posts[i]["answers"] = transform_documents_to_html(answers)

        if "comments" in post:
            comments = post["comments"]
            posts[i]["comments"] = transform_documents_to_html(comments)

    return posts


def copy_and_overwrite(from_path, to_path):
    """Recursively copy and overwrite directory"""
    if os.path.samefile(from_path, to_path):
        return
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
    comments = templateEnv.get_template("comments.jinja")
    main = templateEnv.get_template("main.jinja")
    index = templateEnv.get_template("index.jinja")

    webpage = index.render({
        "posts": json.dumps(archive["posts"]),
        "users": json.dumps(archive["users"]),
        "sidebar_content": sidebar.render(),
        "main_content": main.render({
            "comments_content": comments.render()
        }),
    })

    webpage = minify_html.minify(
        webpage,
        minify_css=True,
        remove_processing_instructions=True
    )

    with open(f"{target_dir}/index.html", "w") as f:
        f.write(webpage)

    copy_and_overwrite(f"{dir_path}/static", f"{target_dir}/static")


if __name__ == "__main__":
    generate_site("assets", "./")


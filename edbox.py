from edapi import EdAPI
from edapi.types.api_types.endpoints.user import API_User_Response_Course
from edapi.types.api_types.course import API_Course
from edapi.types.api_types.thread import API_Thread_WithComments, API_Thread_WithUser, API_User_Short
from edapi.types import EdError
from typing import Generator
from halo import Halo
import time
import json
import pathlib
import os


TIMEOUT_SECONDS = 30
STARTUP_BANNER = r"""
   ____   _____
  / __/__/ / _ )___ __ __
 / _// _  / _  / _ \\ \ /
/___/\___/____/\___/_\_\

"""

class Color:
    MAGENTA   = '\033[95m'
    BLUE      = '\033[94m'
    CYAN      = '\033[96m'
    GREEN     = '\033[92m'
    WARNING   = '\033[93m'
    FAIL      = '\033[91m'
    NC        = '\033[0m'
    BOLD      = '\033[1m'
    UNDERLINE = '\033[4m'


def parse_selection(selection: str, num_classes: int) -> set[int]:
    """Parse user input from the class selection menu."""
    result = set()
    groups = selection.split(",")
    for g in groups:
        pair = g.split("-")
        first, last = int(pair[0]), int(pair[-1])
        if first < 1 or last > num_classes:
            raise ValueError(f"Selection is out of range")
        result.update(range(int(first), int(last)+1))
    return result


def select_courses(courses: list[API_Course]) -> list[API_Course]:
    """
    Prompts the user to choose courses to archive.
    """
    for i, c in enumerate(courses):
        print(f"{i+1}: {c['code']} {c['session']} {c['year']} ({c['id']})")

    print(f"\n{Color.MAGENTA}Enter the classes you would like to archive"+\
          f" as a comma-separated list.\nEntries can be either numbers or"+\
          f" ranges.\nExample: 1,5-7,9-12{Color.NC}")

    try:
        selection = parse_selection(input(">>> "), len(courses))
        return [courses[i-1] for i in sorted(selection)]
    except Exception as e:
        print(f"{Color.FAIL}Invalid selection. {e}{Color.NC}")
        exit(1)


def gen_threads(ed: EdAPI, course_id: int) -> Generator[API_Thread_WithUser, None, None]:
    """Handle pagination and yield threads with user (sidebar feed)"""
    offset = 0
    threads_chunk = ed.list_threads(course_id, limit=100)
    while threads_chunk:
        for thread_with_user in threads_chunk:
            yield thread_with_user
        offset += len(threads_chunk)
        threads_chunk = ed.list_threads(course_id, limit=100, offset=offset)


def archive_course(ed: EdAPI, course: API_Course, spinner: Halo) -> list[API_Thread_WithComments]:
    """Archive all threads from a given course"""
    code = course["code"]
    session = course["session"]
    year = course["year"]
    id = course["id"]
    name = f"{code} {session} {year} ({id})"
    dirname = name.replace("/", " ")
    dirname = "".join(c for c in dirname if c.isalnum() or c == " ")
    dirname = f"archive/{dirname.lower().strip().replace(" ", "-")}"

    print(f"\n{Color.BLUE}Archiving course: {Color.BOLD}{Color.CYAN}{name}{Color.NC}\n")

    results, cnt = [], 0
    pathlib.Path(f"{dirname}/original").mkdir(parents=True, exist_ok=True)
    spinner.start()

    for thread_with_user in gen_threads(ed, id):
        tid = thread_with_user["id"]
        dst = f"{dirname}/original/{tid}.json"
        title_snippet = thread_with_user["title"][:32]
        cnt += 1

        if os.path.isfile(dst):
            spinner.text = f"{cnt} | {Color.WARNING}Already archived:{Color.NC} {title_snippet}..."
            f = open(dst, "r")
            thread_with_comments = API_Thread_WithComments(json.loads(f.read()))
            f.close()
        else:
            spinner.text = f"{cnt} | {Color.MAGENTA}Archiving thread{Color.NC}: {title_snippet}..."
            thread_with_comments = ed.get_thread(thread_with_user["id"])
            f = open(dst, "w")
            f.write(json.dumps(thread_with_comments, indent=2))
            f.close()

        results.append(thread_with_comments)

    with open(f"{dirname}/posts.json", "w") as f:
        f.write(json.dumps(results, indent=2))

    spinner.succeed(f"Successfully archived {len(results)} threads!")
    return results


def main(starting_course_index=0):
    if starting_course_index == 0:
        print(f"{Color.BLUE}{STARTUP_BANNER}{Color.NC}")

    ed = EdAPI()
    try:
        ed.login()
    except Exception as e:
        print(f"{Color.FAIL}Authentication Error: {e}{Color.NC}")
        exit(1)

    spinner = Halo(spinner="dots")
    recovery_course_index = 0

    try:
        user = ed.get_user_info()
        with open("archive/user.json", "w") as f:
            f.write(json.dumps(user, indent=2))

        courses = [c["course"] for c in user["courses"]]
        courses.sort(key=lambda c: c["id"])
        courses = select_courses(courses)

        for i in range(starting_course_index, len(courses)):
            recovery_course_index = i
            archive_course(ed, courses[i], spinner)

    except EdError as e:
        spinner.fail(f"Encountered Ed Error: {e}")
        spinner.spinner = "clock"
        spinner.start()
        for i in range(TIMEOUT_SECONDS, 0, -1):
            spinner.text = f"{Color.FAIL}Timeout, retry in: {i}{Color.NC}"
            time.sleep(1)
        spinner.stop()
        main(recovery_course_index)

    except Exception as e:
        print(f"{Color.FAIL}Encountered exception: {e}{Color.NC}")


if __name__ == "__main__":
    main()

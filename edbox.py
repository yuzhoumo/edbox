import grequests # IMPORTANT: Must be imported before "requests"
import time
import json
import pathlib
import os
import re
import edapi
from urllib.parse import unquote, urlparse
from halo import Halo

# Type definitions
from requests import Response
from typing import Generator
from edapi.types.api_types.course import API_Course
from edapi.types.api_types.thread import API_Thread_WithComments, API_Thread_WithUser, API_User_Short
from edapi.types.api_types.endpoints.threads import API_ListThreads_Response
from edapi.types import EdError
type ThreadGenerator = Generator[API_ListThreads_Response, None, None]
type RequestGenerator = Generator[tuple[int, Response], None, None]


# Global config
ED_USER_AVATAR_BASE_URL = "https://static.us.edusercontent.com/avatars"
ED_CDN_REGEX = r"(?:(?:http[s]?://)?(?:static\.us\.edusercontent\.com))/files/[^\\\'\"\s)]*"
OUT_DIR = "out"
TIMEOUT_SECONDS = 30
STARTUP_BANNER = r"""
   ____   _____
  / __/__/ / _ )___ __ __
 / _// _  / _  / _ \\ \ /
/___/\___/____/\___/_\_\

"""


class PatchedEdAPI(edapi.EdAPI):
    @edapi.edapi._ensure_login
    def patched_list_threads(
        self, /, course_id: int, *, limit: int = 30, offset: int = 0, sort: str = "new"
    ) -> API_ListThreads_Response:

        from edapi.edapi import API_BASE_URL, _throw_error
        from edapi.edapi import urljoin

        list_url = urljoin(API_BASE_URL, f"courses/{course_id}/threads")
        response = self.session.get(
            list_url, params={"limit": limit, "offset": offset, "sort": sort}
        )
        if response.ok:
            return response.json()

        _throw_error(
            f"Failed to list threads for course {course_id}.", response.content
        )

ed = PatchedEdAPI() # Global ed client

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


def gen_threads(course_id: int) -> ThreadGenerator:
    """Handle pagination and yield threads with user (sidebar feed)"""
    offset = 0
    chunk = ed.patched_list_threads(course_id, limit=100)
    while chunk["threads"]:
        yield chunk
        offset += len(chunk["threads"])
        chunk = ed.patched_list_threads(course_id, limit=100, offset=offset)


def gen_get_requests(reqs: list[grequests.AsyncRequest]) -> RequestGenerator:
    """Generator for fetching files"""
    # Fetch asynchronously, 6 at a time
    for i, res in grequests.imap_enumerated(reqs, size=6):
        filename = os.path.split(reqs[i].url)[1]
        if res is None:
            raise ConnectionError(f"Failed to get: {filename}")
        yield i, res


def extract_filename(res: Response) -> str:
    """Parse url encoded filename from header and return decoded filename"""
    cd = res.headers["content-disposition"]
    encoded_filename = re.findall("filename=\"(.+)\"", cd)[0]
    decoded_filename = unquote(encoded_filename)
    return decoded_filename


def archive_thread_files(base_dir: str, thread: API_Thread_WithComments, spinner: Halo) -> str:
    """
    Archive all static files from a thread and return new json string with
    converted links.
    """
    thread_json = json.dumps(thread)
    links = list(set(re.findall(ED_CDN_REGEX, thread_json)))
    parsed_links = [urlparse(link) for link in links]

    links_to_archive = []
    for link, pl in zip(links, parsed_links):
        if not os.path.isdir(f"{base_dir}{pl.path}"):
            links_to_archive.append((link, pl))

    cnt, total = 1, len(links_to_archive)
    old_spinner_text = spinner.text
    reqs = [grequests.get(link) for link, _ in links_to_archive]
    for i, res in gen_get_requests(reqs):
        link, pl = links_to_archive[i] # Indices come back in arbitrary order
        filename = extract_filename(res)
        status = f"{cnt}/{total} | {Color.MAGENTA}Archiving file{Color.NC}: {filename}"
        spinner.text = f"{old_spinner_text} <<< {status}"
        cnt += 1

        dir = f"{base_dir}{pl.path}"
        pathlib.Path(dir).mkdir(parents=True, exist_ok=True)
        f = open(f"{dir}/{filename}", "wb")
        f.write(res.content)
        f.close()
        os.listdir(dir)[0]

    for link, pl in zip(links, parsed_links):
        path = f"{base_dir}{pl.path}"
        filename = os.listdir(path)[0]
        thread_json = thread_json.replace(link, f"{pl.path.strip("/")}/{filename}")

    return thread_json


def archive_thread(base_dir: str, thread_with_user: API_Thread_WithUser, spinner: Halo, cnt: int):
    """Archive a single discussion thread"""
    tid = thread_with_user["id"]
    dst = f"{base_dir}/original/{tid}.json"
    title_snippet = thread_with_user["title"][:32]

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

    return archive_thread_files(base_dir, thread_with_comments, spinner)


def archive_user_avatars(base_dir: str, users: list[API_User_Short], spinner: Halo):
    """Archive user profile photos"""
    reqs, users_to_archive = [], []
    for user in users:
        avatar = user["avatar"]
        if avatar is None or os.path.isfile(f"{base_dir}/avatars/{avatar}.jpg"):
            continue
        reqs.append(grequests.get(f"{ED_USER_AVATAR_BASE_URL}/{avatar}"))
        users_to_archive.append(user)

    dir = f"{base_dir}/avatars"
    pathlib.Path(dir).mkdir(parents=True, exist_ok=True)

    cnt, total = 1, len(users_to_archive)
    for i, res in gen_get_requests(reqs):
        user = users_to_archive[i]
        spinner.text = f"{cnt}/{total} | {Color.MAGENTA}Archiving user photo: {user["name"]}{Color.NC}"
        cnt += 1

        f = open(f"{dir}/{user["avatar"]}.jpg", "wb")
        f.write(res.content)
        f.close()


def archive_course(course: API_Course, spinner: Halo) -> list[API_Thread_WithComments]:
    """Archive all threads from a given course"""
    name = f"{course["code"]} {course["session"]} {course["year"]} ({course["id"]})"
    dirname = name.replace("/", " ")
    dirname = "".join(c for c in dirname if c.isalnum() or c == " ")
    dirname = f"{OUT_DIR}/{dirname.lower().strip().replace(" ", "-")}"

    print(f"\n{Color.BLUE}Archiving course: {Color.BOLD}{Color.CYAN}{name}{Color.NC}\n")

    users = []
    results, cnt = [], 1
    pathlib.Path(f"{dirname}/original").mkdir(parents=True, exist_ok=True)
    spinner.start()

    for res in gen_threads(course["id"]):
        users.extend(res["users"])
        for thread_with_user in res["threads"]:
            thread_json = archive_thread(dirname, thread_with_user, spinner, cnt)
            results.append(json.loads(thread_json))
            cnt += 1

    with open(f"{dirname}/posts.json", "w") as f:
        f.write(json.dumps(results, indent=2))

    archive_user_avatars(dirname, users, spinner)
    with open(f"{dirname}/users.json", "w") as f:
        f.write(json.dumps(users, indent=2))

    spinner.succeed(f"Successfully archived {len(results)} threads!")
    return results


def main(courses: list[API_Course] = []):
    spinner = Halo(spinner="dots")
    current_course_index = 0

    try:
        user = ed.get_user_info()
        pathlib.Path(OUT_DIR).mkdir(parents=True, exist_ok=True)
        with open(f"{OUT_DIR}/user.json", "w") as f:
            f.write(json.dumps(user, indent=2))

        if len(courses) == 0:
            courses = select_courses([c["course"] for c in user["courses"]])
            courses.sort(key=lambda c: c["id"])

        for i, course in enumerate(courses):
            current_course_index = i
            archive_course(course, spinner)

    except EdError as e:
        spinner.fail(f"Encountered Ed Error: {e}")
        spinner.spinner = "clock"
        spinner.start()
        for i in range(TIMEOUT_SECONDS, 0, -1):
            spinner.text = f"{Color.FAIL}Timeout, retry in: {i}{Color.NC}"
            time.sleep(1)
        spinner.stop()
        main(courses[current_course_index:])

    except Exception as e:
        print(f"{Color.FAIL}Encountered exception: {e}{Color.NC}")


if __name__ == "__main__":
    print(f"{Color.BLUE}{STARTUP_BANNER}{Color.NC}")

    try:
        ed.login()
    except Exception as e:
        print(f"{Color.FAIL}Authentication Error: {e}{Color.NC}")
        exit(1)

    main()

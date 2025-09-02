# import os
# import requests
# from bs4 import BeautifulSoup
# from dotenv import load_dotenv

# load_dotenv()

# LOGIN_URL = "https://lmsug23.iiitkottayam.ac.in/login/index.php"

# def login_to_lms():
#     session = requests.Session()
#     # Get login token
#     login_page = session.get(LOGIN_URL)
#     soup = BeautifulSoup(login_page.text, 'html.parser')
#     token = soup.find("input", {"name": "logintoken"})["value"]

#     payload = {
#         "username": os.getenv("LMS_USERNAME"),
#         "password": os.getenv("LMS_PASSWORD"),
#         "logintoken": token
#     }

#     response = session.post(LOGIN_URL, data=payload)
#     if "login" in response.url:
#         raise Exception("Login failed! Check credentials.")
    
#     return session

# def get_attendance_for_course(session, url):
#     response = session.get(url)
#     soup = BeautifulSoup(response.text, 'html.parser')
    
#     # Course name
#     course_name_tag = soup.select_one('h1')
#     course_name = course_name_tag.text.strip() if course_name_tag else "Unknown Course"
    
#     # Parse table
#     table = soup.find("table", {"class": "generaltable"})
#     total_classes = present = 0
#     if table:
#         rows = table.find_all("tr")[1:]
#         for row in rows:
#             cols = row.find_all("td")
#             if len(cols) >= 3:
#                 status = cols[2].get_text(strip=True)
#                 if status != '?':
#                     total_classes += 1
#                 if status.lower() == "present":
#                     present += 1
#     percentage = (present / total_classes * 100) if total_classes > 0 else 0
#     return {
#         "course": course_name,
#         "total_classes": total_classes,
#         "present": present,
#         "absent": total_classes - present,
#         "percentage": round(percentage, 2)
#     }

# def get_all_attendance():
#     session = login_to_lms()
#     urls = os.getenv("Batch-3-COURSE_URLS").split(",")
#     data = {}
#     for url in urls:
#         result = get_attendance_for_course(session, url.strip())
#         data[result["course"]] = {
#             "total_classes": result["total_classes"],
#             "present": result["present"],
#             "absent": result["absent"],
#             "percentage": result["percentage"]
#         }
#     return data


# main.py
import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

LOGIN_URL = "https://lmsug23.iiitkottayam.ac.in/login/index.php"
NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def login_to_lms():
    session = requests.Session()
    login_page = session.get(LOGIN_URL)
    soup = BeautifulSoup(login_page.text, 'html.parser')
    token = soup.find("input", {"name": "logintoken"})["value"]

    payload = {
        "username": os.getenv("LMS_USERNAME"),
        "password": os.getenv("LMS_PASSWORD"),
        "logintoken": token
    }

    response = session.post(LOGIN_URL, data=payload)
    if "login" in response.url:
        raise Exception("Login failed! Check credentials.")
    
    return session

def get_attendance_for_course(session, url):
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    course_name_tag = soup.select_one('h1')
    course_name = course_name_tag.text.strip() if course_name_tag else "Unknown Course"
    
    table = soup.find("table", {"class": "generaltable"})
    total_classes = present = 0
    if table:
        rows = table.find_all("tr")[1:]
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                status = cols[2].get_text(strip=True)
                if status != '?':
                    total_classes += 1
                if status.lower() == "present":
                    present += 1
    percentage = (present / total_classes * 100) if total_classes > 0 else 0
    return {
        "course": course_name,
        "total_classes": total_classes,
        "present": present,
        "absent": total_classes - present,
        "percentage": round(percentage, 2)
    }

def get_all_attendance():
    session = login_to_lms()
    urls = os.getenv("COURSE_URLS").split(",")
    data = []
    for url in urls:
        result = get_attendance_for_course(session, url.strip())
        data.append(result)
    return data

# --- NEW: Push results to Notion ---
def push_to_notion(data):
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    for course in data:
        payload = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": {
                "Course Name": {"title": [{"text": {"content": course['course']}}]},
                "Attendance %": {"number": course['percentage']},
                "Total Classes": {"number": course['total_classes']},
                "Present": {"number": course['present']},
                "Absent": {"number": course['absent']}
            }
        }
        res = requests.post("https://api.notion.com/v1/pages", headers=headers, json=payload)
        print("Notion response:", res.status_code, res.text)

if __name__ == "__main__":
    attendance_data = get_all_attendance()
    push_to_notion(attendance_data)
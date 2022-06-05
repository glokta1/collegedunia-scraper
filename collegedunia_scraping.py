import requests
import base64
import csv
import json
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0'
}

details_list = []

# Fetch page from Collegedunia's API
def get_api_endpoint_of_page(page):
    base_url = "https://collegedunia.com/web-api/listing?data="
    encoded_key = encode_to_base_sixty_four(f'{{"url":"india-colleges","page":{page}}}')
    page_url = base_url + encoded_key
    print(f'page: {page}, {page_url}')
    return page_url
    
def encode_to_base_sixty_four(key):
    return base64.b64encode(bytes(key, 'utf-8')).decode('ascii')

def get_response_from_page(page_url):
    page = requests.get(page_url, headers=headers).json()

    colleges = page['colleges']

    for college in colleges:
        sub_url = college['url']
        college_url = f"https://collegedunia.com/web-api/{sub_url}"
        details = get_response_from_college(college_url)
        details_list.append(details)


def get_response_from_college(college_url):
    college = requests.get(college_url, headers=headers).json()

    try:
        name = college['college_name']
        approved_by = college['basic_info']['approved_by']
        if len(approved_by) == 1:
            approved_by = approved_by[0]
        else:
            approved_by = ""
            for organization in approved_by:
                approved_by += f'{organization}, '
        estd = college['basic_info']['year_founded']

        city = college['basic_info']['city']
        state = college['basic_info']['state']
        location = f"{city}, {state}"

        rank = college['basic_info']['ranking'][0]['rank']
        stream = college['basic_info']['ranking'][0]['stream']
        year = college['basic_info']['ranking'][0]['year']
        agency = college['basic_info']['ranking'][0]['agency']
        rank_info = f"Ranked {rank} for {stream} by {agency} {year}"

        courses = college['course_data']['courses']
        fee_info = ""
        for course in courses:
            course_name = course['short_head']
            course_fee = course['fees_data']['amount']
            fee_info += f"{course_name}: \u20B9{course_fee}\n"

        photos = college['gallery']['photo_list']
        first_photo = list(photos.values())[0][0]['iamge_path']     # yes, it's iamge. It's a typo in the API
    except Exception as e:
        name = None
        rank = None
        first_photo = None
        rank_info = 'Rank data not available'
        fee_info = 'Fee details not found'
    
    details = [name, location, estd, approved_by, rank_info, fee_info, first_photo]
    return details;

with open("colleges.csv", "w", encoding='UTF8') as csv_file:
    titles = ["Name", "Location", "Estd.", "Approved By", "Rank", "Courses and Fees", "Photo"]
    writer = csv.writer(csv_file)

    writer.writerow(titles)
    last_page_number = 1852
    for page in range(1, 5):
        # to deal with rate limiting (doesn't work rn)
        if (page % 30 == 29):
            time.sleep(300)
        page_url = get_api_endpoint_of_page(page)
        get_response_from_page(page_url)

    writer.writerows(details_list)


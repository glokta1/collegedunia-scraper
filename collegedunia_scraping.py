import requests
import base64
import csv
import json
import time
import os
import random

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:100.0) Gecko/20100101 Firefox/100.0'
}


details_list = []
countries_list = ['Germany','UK','Singapore']

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
    page_response = requests.get(page_url, headers=headers)
    page = page_response.json()

    try:
        colleges = page['colleges']

        for college in colleges:
            sub_url = college['url']
            college_url = f"https://collegedunia.com/web-api/{sub_url}"
            details = get_response_from_college(college_url)
            details_list.append(details)
    except Exception:
        pass


def get_response_from_college(college_url):
    college_response = requests.get(college_url, headers=headers) 
# print(f'Response code: {college_response.status_code}')
    college = college_response.json()
    
    try:
        name = college['college_name']
    except Exception:
        name = "No name found"
    try:
        approved_by = college['basic_info']['approved_by']
    except Exception:
        approved_by = ""

    if len(approved_by) == 1:
        approved_by = approved_by[0]
    else:
        approved_by = ""
        for organization in approved_by:
            approved_by += f'{organization}, '
    try:
        estd = college['basic_info']['year_founded']
    except Exception:
        estd = "Not found"

    try:
        city = college['basic_info']['city']
    except Exception:
        city = "No city found"
    try:
        state = college['basic_info']['state']
    except:
        state = "No state found"

    try:
        address = college['basic_info']['address']['location'].rstrip(",")
        if len(address) == 0:
            address = "No address found"
    except Exception:
        address = "No address found"

    try:
        rank = college['basic_info']['ranking'][0]['rank']
        stream = college['basic_info']['ranking'][0]['stream']
        year = college['basic_info']['ranking'][0]['year']
        agency = college['basic_info']['ranking'][0]['agency']
        rank_info = f"Ranked {rank} for {stream} by {agency} {year}"
    except Exception:
        rank_info = "rank data not available"

    try:
        courses = college['course_data']['courses']
        fee_info = ""
        for course in courses:
            course_name = course['short_head']
            course_fee = course['fees_data']['amount']
            fee_info += f"{course_name}: \u20B9{course_fee}\n"
    except Exception:
        fee_info = "No data found"

    try:
        photos = college['gallery']['photo_list']
        first_photo = list(photos.values())[0][0]['iamge_path']     # yes, it's iamge. It's a typo in the API
    except Exception:
        photos = None
        first_photo = "No photo available"

    try:
        category = college['basic_info']['major_stream_name']
    except Exception:
        category = "No category found"
    
    try:
        affiliated_uni = college['basic_info']['affiliated_to']['name']
    except Exception:
        affiliated_uni = "N/A"

    try:
        brochures = college['brochure']
        brochure_info = ""
        if len(brochures) == 0:
            brochure_info = "No brochure found"
        else:
            for brochure in brochures:
                pdf_sub_link = brochure['link']
                brochure_url = f'https://images.collegedunia.com/public/college_data/images/pdfcol/{pdf_sub_link}'
                brochure_name = brochure['name']
                brochure_info += f"{brochure_name}: {brochure_url}\n"
    except Exception:
        brochure_info = "No brochure found"

    try:
        phone_number = college['basic_info']['phone_no'][0]['value']
    except Exception:
        phone_number = "No number found"

    try:
        email_raw = college['schemaJsonLd']['2'].split(",")[5]
        if "null" not in email_raw:
            email = college['schemaJsonLd']['2'].split(",")[5].replace("\"email\":", "").strip("\"")
        else:
            email = "No email found"
    except:
        email = "No email found"
    
    details = [name, category, address, city, state, estd, approved_by, affiliated_uni, rank_info, fee_info, email, phone_number, first_photo, brochure_info]
    return details;

flag = 0;

def switch_ip():
    global flag
    try:
        if flag == 0:
            os.system("nordvpn c " + random.choice(countries_list))
            flag = 1
        else:
            os.system("nordvpn disconnect")
            flag = 0
    except Exception:
        print("sorry, vpn can't connect")

with open("colleges.csv", "a", encoding='UTF8') as csv_file:
    titles = ["Name", "Category", "Address", "City", "State", "Estd", "Approved By", "Affiliated University", "Rank", "Courses and Fees", "Email", "Phone Number", "Photo", "Brochure"]
    writer = csv.writer(csv_file)

    writer.writerow(titles)
    last_page_number = 1852
    start = 1
    for page in range(start, last_page_number + 1):
        if (page-start) % 30 == 29:
            # switch_ip()
            time.sleep(360)
        page_url = get_api_endpoint_of_page(page)
        get_response_from_page(page_url)

    writer.writerows(details_list)
    os.system("nordvpn disconnect")

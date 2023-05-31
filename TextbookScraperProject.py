import json
import requests
from bs4 import BeautifulSoup
import os.path
import xml.etree.ElementTree as ET
import re
import itertools
import time


# Textbook URL
url = "https://epub-factory-cdn.mheducation.com/publish/sn_f90ad/25/1080mp4/OPS/s9ml/chapter34/reader01.xhtml"
requestResponse = ""
acessDeniedCount = 0
retrivedText = []
cookies = {}


# Cookies
CloudFront_Signature = ""
CloudFront_Policy = ""
CloudFront_Key_Pair_Id = ""
MH_TOKEN = ""                   # MH_TOKEN isn't used, but required to have in request so it's filled with a "nil" string


# checks if cookie file exists and reads it
def checkCookies():
    # checks if cookie file exists
    if os.path.isfile("cookies.txt"):
        print("Cookie file found")

        # Open cookies.txt
        with open("cookies.txt", "r") as f:
            # reads all lines into a lis
            lines = f.readlines()

        # iterates through lines
            for line in lines:

                if "CloudFront_Policy" in line:
                    # CloudFront_Policy
                    CloudFront_Policy = (line.split("CloudFront_Policy=", 1)[1]).strip()            #split finds "CloudFront_Policy=", strip removes newline
                    # print("CloudFront_Policy:", CloudFront_Policy, "\n")

                elif "CloudFront_Signature" in line:
                    # CloudFront_Signature
                    CloudFront_Signature = (line.split("CloudFront_Signature=", 1)[1]).strip()
                    # print("CloudFront_Signature:", CloudFront_Signature, "\n")

                elif "CloudFront_Key_Pair_Id" in line:
                    # CloudFront_Key_Pair_Id
                    CloudFront_Key_Pair_Id = (line.split("CloudFront_Key_Pair_Id=", 1)[1]).strip()
                    # print("CloudFront_Key_Pair_Id:", CloudFront_Key_Pair_Id, "\n")

                elif "MH_TOKEN" in line:
                    # MH_TOKEN
                    MH_TOKEN = (line.split("MH_TOKEN=", 1)[1]).strip()
                    # print("MH_TOKEN:", MH_TOKEN, "\n")

            # Checks if none are empty
            if CloudFront_Policy == "" or CloudFront_Signature == "" or CloudFront_Key_Pair_Id == "" or MH_TOKEN == "":
                print("Error: One or more cookies are empty.")
                exit()
            else:
                print("Cookie Reading Success!")
                
                # makes cookies global so that you can put cookies.txt info into it
                global cookies
                cookies = {
                'CloudFront-Key-Pair-Id': CloudFront_Key_Pair_Id,
                'CloudFront-Signature': CloudFront_Signature,
                'CloudFront-Policy': CloudFront_Policy,
                'MH_TOKEN': MH_TOKEN,                               # MH_TOKEN isn't used
                }
                # print("Cookies: ", cookies)

    else: 
        print("ERROR: cookie file not found\n")
        print("Check if cookie.txt exists in directory")
        exit()

# checks if the textbook returns an access denied error
def checkForAccess():
    global requestResponse
    requestResponse = requests.get(url, cookies=cookies)      # creates and sends request

    if requestResponse.status_code == 200:
        print("Web Request Success!")
        return "success"
    elif requestResponse.status_code == 403:
        return "accessDenied"
    else:
        return "error"
    
# parse the textbook
def parseTextbook():
    global requestResponse

    html = requestResponse.text    # HTML = r.text
    soup = BeautifulSoup(html, 'html.parser')   #Parses html with BeautifulSoup

    # Variables for headings (used in json)
    topic = "Topic: "
    head = "Heading: "
    subhead = "Subheading: "

    # Dictionary stores topics, subheadings, subsubheadings
    topics = {}

    for h2 in soup.find_all('h2'):
        # topic_name = f"{topic} {h2.text.strip()}"           #Json Formatting: "Topic: Topic Name"
        topic_name = h2.text.strip()
        topics[topic_name] = {}

        for h3 in h2.find_next_siblings('h3'):
            # subheading_name = f"{head} {h3.text.strip()}"
            subheading_name = h3.text.strip()
            topics[topic_name][subheading_name] = {}
            for h4 in h3.find_next_siblings('h4'):
                # subsubheading_name = f"{subhead} {h4.text.strip()}"
                subsubheading_name = h4.text.strip()
                text = h4.find_next_sibling('p').text.strip()
                topics[topic_name][subheading_name][subsubheading_name] = text
            # if not topics[topic_name][subheading_name]:
                # text = h3.find_next_sibling('p').text.strip()
                # topics[topic_name][subheading_name] = text

    # Print the resulting mapping
    r = json.dumps(topics, indent=4)
    print(r)

    global retrivedText
    retrivedText.append(r)
    


### DEPRECATED ###
# permutation for cookies, if order of cookies has changed
# def permCookies():
    # keys = list(cookies.keys())
    # combinations = list(itertools.permutations(keys))
# 
    # for combination in combinations:
        # values = [cookies[key] for key in combination]
        # print("dict(zip): ", dict(zip(combination, values)))

# cycles through reader pages (ie. 01-13)
def iterateReaders():
    global url
    rgx = "https:\/\/epub-factory-cdn\.mheducation\.com\/publish\/\S+\/chapter\d+\/reader([0-9]{2}).xhtml"
    x = re.search(rgx, url)

    if x:
        print("Regex: ", x[1])
        if int(x[1]) > 1:
            print("more than 1")
        else:
            print("equal to 1")

            for i in range(10):
                if i < 10:
                    num = f"0{i}"
                else:
                    num = f"{i}"
                url = f"https://epub-factory-cdn.mheducation.com/publish/sn_f90ad/25/1080mp4/OPS/s9ml/chapter34/reader{num}.xhtml"
                print("URL: ", url)
                parse()
                print(f"Success! reader{i}")
                time.sleep(5)

def parse():
    # Request to textbook (with cookies)
    r = requests.get(url, cookies=cookies)

    # Parses the HTML
    if r.status_code == 200:
        print("Web Request Success!")
        # print("Web Request Success Cookies: ", cookies)
        html = r.text    # HTML = r.text
        
        soup = BeautifulSoup(html, 'html.parser')   #Parses html with BeautifulSoup

        # Variables for headings (used in json)
        topic = "Topic: "
        head = "Heading: "
        subhead = "Subheading: "

        # Dictionary stores topics, subheadings, subsubheadings
        topics = {}

        for h2 in soup.find_all('h2'):
            # topic_name = f"{topic} {h2.text.strip()}"           #Json Formatting: "Topic: Topic Name"
            topic_name = h2.text.strip()
            topics[topic_name] = {}

            for h3 in h2.find_next_siblings('h3'):
                # subheading_name = f"{head} {h3.text.strip()}"
                subheading_name = h3.text.strip()
                topics[topic_name][subheading_name] = {}

                for h4 in h3.find_next_siblings('h4'):

                    # subsubheading_name = f"{subhead} {h4.text.strip()}"
                    subsubheading_name = h4.text.strip()
                    text = h4.find_next_sibling('p').text.strip()
                    topics[topic_name][subheading_name][subsubheading_name] = text
                # if not topics[topic_name][subheading_name]:
                    # text = h3.find_next_sibling('p').text.strip()
                    # topics[topic_name][subheading_name] = text

        # Print the resulting mapping
        r = json.dumps(topics, indent=4)
        print(r)

        global retrivedText
        retrivedText.append(r)
 

    # error handling
    else:
        print("Error: " + str(r.status_code))
        # print("Content: " + str(r.content))
        # print("Headers: " + str(r.headers))

        # Gets XML HTTP response
        response = r.content

        # Parse the XML response
        root = ET.fromstring(response)

        # Get the value of the Code element
        error_code = root.find('Code').text

        print("ERRORORRR CODDDDEEEEE: ", error_code)
        print("Cookies after perm: ", cookies)

        # Check if the error code is AccessDenied
        if error_code == 'AccessDenied':
            print("Access Denied Error\n")
            print("Usually this means that your cookies have expired. \nTry logging in, obtaining new cookies, and putting them into cookies.txt")

            time.sleep(1)

            global acessDeniedCount     # so acessDeniedCount can be accessed
            acessDeniedCount += 1
            print("Denied count: ", acessDeniedCount)
            print("Error CODDDDE: ", error_code)

            # changes order of cookies to see if that's the issue (sometimes MGH changes the order in which cookies are required)
            if acessDeniedCount > 0:  # 16 total permuatations of cookies (4 * 4 = 16)
                print("Error, access still denied")
                print("Check if your cookies have expired. Usually, the KEY-PAIR-ID doesn't change, so check the CloudFront_Signature, CloudFront_Policy, and MH_TOKEN")
                
            else:
                # permCookies()
                parse()


# runs stuff
# if "__main__" == __name__:
    # print("yey")
    # iterateReaders()
    # parse()
    #print("retrived Text: ", retrivedText)

    # Write to json file
    # with open('data.json', 'w') as outfile:
        # outfile.write(str(retrivedText)) 


# This entire file is a mess and it needs to be completely rewritten.
# Turns out that MH_TOKEN isn't used

if "__main__" == __name__:
    print("yey\n")

    checkCookies()
    status = checkForAccess()

    if status == "success":
        # parse textbook
        parseTextbook()
    elif status == "acessDenied":
        # Tell user acess is denied
        print("Access Denied Error")
        print("Try checking of the cookies are outdated")
    # print("Cookies: ", cookies)
    # TODO
    # 1. Func to iterate through all the readers (ie. 01-13)
    # 2. 

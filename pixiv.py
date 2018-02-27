import threading
from lxml import etree
import requests
import re


def login(session, username, passwd):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36"}
    data = {"source": "pc", "ref": "wwwtop_accounts_index", "return_to": "https://www.pixiv.net/"}

    s=session
    logintext = s.get("https://accounts.pixiv.net/login").text
    get_key = re.compile('''(?<="post_key" value=")\w+''')
    post_key = get_key.search(logintext).group(0)
    data["post_key"] = post_key
    data["pixiv_id"] = username
    data["password"] = passwd
    return s.post("https://accounts.pixiv.net/login",headers=headers,data=data)


def addReferer(url):
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36",
             "Host": "i.pximg.net",
             "Accept": "image / webp, image / apng, image / *, * / *;q = 0.8"
    }
    headers['Referer'] =url
    return headers


def write_image(url, headers, title):
    image = requests.get(url, headers=headers).content
    title=title+".jpg"
    with open(title,"wb") as f:
        f.write(image)


def ImageURL(session, url):
    s=session
    url="https://www.pixiv.net/"+url
    url_content = (etree.HTML(s.get(url).content))
    is_manga = url_content.xpath('//*[@id="wrapper"]/div[1]/div[1]/div/div[4]/a[2]/@data-click-label')
    if is_manga==[]:
        image_url=url_content.xpath(
        '//body/div[@id="wrapper"]/div[@class="_illust_modal _hidden ui-modal-close-box"]//@data-src')[0]
        headers = addReferer(url)
        title=url_content.xpath('//*[@id="wrapper"]//h1/text()')[0]
        return image_url, headers, title
    else:
        pass
        return None,None,None


def downloadImage(session, illust_url):
    s=session
    image_url, headers, title=ImageURL(s, illust_url)
    if image_url:
        write_image(image_url, headers, title)
        print(title+" downloaded")


def urlList(session, page_num):
    s=session
    favourite_page = s.get("https://www.pixiv.net/bookmark.php?p="+str(page_num)).content
    favourite_page = etree.HTML(favourite_page)
    linklist = favourite_page.xpath(r'//*[@id="wrapper"]/div[1]/div[1]/div[1]/form/div[1]/ul/li/a[@style="display:block"]/@href')
    return linklist


def pixiv():
    s = requests.Session()
    name = input("please input username:")
    passwd = input("please input passwd:")
    login(s, name, passwd)
    start_page = input("please input start page:")
    end_page = input("please input end page:")
    linklist = []
    for page in range(int(start_page), int(end_page) + 1):
        linklist += urlList(s, page)

    # for link in linklist:
    #     downloadImage(s, link)
    for i in range(len(linklist)):
        thread = threading.Thread(target = downloadImage, args = (s,linklist[i]))
        thread.start()
    


if __name__=="__main__":
    pixiv()

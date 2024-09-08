import os
import time
import requests
from bs4 import BeautifulSoup
import spacy
import pytextrank

# Hàm tải ảnh từ URL
def download_image(url, file_name):
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(response.content)

# Function to scrape images by keyword
def scrape_images(keyword, index, num_images=6):
    # Create a directory to save images
    folder_save = f"Segment/{index + 1}"
    if not os.path.exists(folder_save):
        os.makedirs(folder_save)

    search_url = f"https://www.bing.com/images/search?q={keyword}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Edg/128.0.0.0"}

    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Tìm tất cả thẻ ảnh từ kết quả trả về
    images = soup.find_all("a", {"class": "iusc"})
    img_urls = []

    # Lọc các ảnh từ kết quả và lấy URL ảnh lớn
    for image in images:
        m = image.get("m")
        if m:
            m = eval(m)  # Chuyển đổi chuỗi JSON thành dictionary
            img_url = m.get("murl")
            if img_url:
                img_urls.append(img_url)
            if len(img_urls) >= num_images:
                break

    # Tải các ảnh đã tìm thấy
    for img_url in img_urls:
        timestamp = int(time.time() * 1000)  # Milliseconds precision
        save_path = os.path.join(folder_save, f"{timestamp}.jpg")
        download_image(img_url, save_path)
        print(f"Downloaded {img_url}")

def get_keyword(text, keyword_main=""):
    result = ""
    # load a spaCy model, depending on language, scale, etc.
    nlp = spacy.load("en_core_web_sm")
    # add PyTextRank to the spaCy pipeline
    nlp.add_pipe("textrank")
    doc = nlp(text)

    if(keyword_main != ""):
        # examine the top-ranked phrases in the document
        for phrase in doc._.phrases[:5]:
            # Nếu phrase.text chứa "Megan" thì chuyển từ đó thành "Meghan"
            if "Megan" in phrase.text:
                phrase.text = phrase.text.replace("Megan", "Meghan")
            if phrase.text in keyword_main:
                continue
            result += phrase.text + ", "
        result = result + keyword_main 
    else:
        # examine the top-ranked phrases in the document
        for phrase in doc._.phrases[:2]:
            # Nếu phrase.text chứa "Megan" thì chuyển từ đó thành "Meghan"
            if "Megan" in phrase.text:
                phrase.text = phrase.text.replace("Megan", "Meghan")
            result += phrase.text + ", "
    return result

# Usage
if __name__ == "__main__":
    lines = []
    with open("E.txt", 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip() == '':
                continue
            else:
                lines.append(line.strip())

    keyword_main = get_keyword(lines[0])
    for i in range(len(lines)):
        if(i == 20):
            break
        keyword = get_keyword(lines[i], keyword_main)
        print(i+1, keyword)
        scrape_images(keyword, i, num_images=6)
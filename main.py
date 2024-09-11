import os
import time
import requests
from bs4 import BeautifulSoup
import spacy
import pytextrank
import tkinter as tk
from tkinter import filedialog, messagebox

# Hàm tải ảnh từ URL
def download_image(url, file_name):
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(response.content)

# Function to scrape images by keyword
def scrape_images(keyword, index, folder_save, num_images=6):
    folder_segment = f"{folder_save}/{index + 1}"
    if not os.path.exists(folder_segment):
        os.makedirs(folder_segment)

    search_url = f"https://www.bing.com/images/search?q={keyword}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Edg/128.0.0.0"}

    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Tìm tất cả thẻ ảnh từ kết quả trả về
    images = soup.find_all("a", {"class": "iusc"})
    img_urls = 0

    # Lọc các ảnh từ kết quả và lấy URL ảnh lớn
    for image in images:
        m = image.get("m")
        if m:
            m = eval(m)  # Chuyển đổi chuỗi JSON thành dictionary
            img_url = m.get("murl")
            if img_url:
                timestamp = int(time.time() * 1000)  # Milliseconds precision
                save_path = os.path.join(folder_segment, f"{timestamp}.jpg")
                try:
                    download_image(img_url, save_path)
                    img_urls += 1
                except:
                    print("Error")
                    pass
            if img_urls >= num_images:
                break

    
        

def get_keyword(text, keyword_main=""):
    result = ""
    nlp = spacy.load("en_core_web_sm")
    nlp.add_pipe("textrank")
    doc = nlp(text)

    if keyword_main != "":
        for phrase in doc._.phrases[:5]:
            if "Megan" in phrase.text:
                phrase.text = phrase.text.replace("Megan", "Meghan")
            if phrase.text in keyword_main:
                continue
            result += phrase.text + ", "
        result = result + keyword_main 
    else:
        for phrase in doc._.phrases[:2]:
            if "Megan" in phrase.text:
                phrase.text = phrase.text.replace("Megan", "Meghan")
            result += phrase.text + ", "
    return result

def count_characters_in_text(text):
    stripped_line = text.strip()
    if stripped_line:  
        return len(stripped_line), str(len(stripped_line))[0]
    return 0, 0

# Hàm chọn file văn bản
def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        entry_file.delete(0, tk.END)
        entry_file.insert(0, file_path)

# Hàm chọn thư mục lưu
def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        entry_folder.delete(0, tk.END)
        entry_folder.insert(0, folder_path)

# Hàm bắt đầu xử lý
def start_processing():
    file_path = entry_file.get()
    folder_save = entry_folder.get()

    if not file_path or not folder_save:
        messagebox.showerror("Lỗi", "Vui lòng chọn file và thư mục lưu ảnh!")
        return

    lines = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip() == '':
                continue
            else:
                lines.append(line.strip())

    label_status.config(text="Đang xử lý...", fg="blue")
    root.update()  # Cập nhật giao diện
    keyword_main = get_keyword(lines[0])
    # Mở file log.txt ở chế độ ghi (write) để làm trống file
    with open("log.txt", "w", encoding='utf-8') as log_file:
        log_file.write("")  # Xóa nội dung của file
        
    # Mở file log.txt ở chế độ ghi (append)
    with open("log.txt", "a", encoding='utf-8') as log_file:
        for i in range(len(lines)):
            if i == 20:
                break
            keyword = get_keyword(lines[i], keyword_main)
            len_text, first_character = count_characters_in_text(lines[i])
            if(len_text < 100):
                first_character = 1
            print(i+1, keyword)
            print(f"Length: {len_text}, Image number: {first_character}")
            # Ghi vào log.txt
            log_file.write(f"{i+1}. Keyword: {keyword}\n")
            log_file.write(f"Length: {len_text}, Image number: {first_character}\n\n")
            
            scrape_images(keyword, i, folder_save, num_images=int(first_character))
            

        label_status.config(text="Xử lý thành công!", fg="green")
    

# Tạo giao diện
root = tk.Tk()
root.title("Ứng dụng Tải Ảnh Từ Từ Khóa")

# Tạo các thành phần giao diện
label_file = tk.Label(root, text="Chọn file văn bản (.txt):")
label_file.grid(row=0, column=0, padx=10, pady=10)

entry_file = tk.Entry(root, width=50)
entry_file.grid(row=0, column=1, padx=10, pady=10)

button_file = tk.Button(root, text="Chọn file", command=select_file)
button_file.grid(row=0, column=2, padx=10, pady=10)

label_folder = tk.Label(root, text="Chọn thư mục lưu:")
label_folder.grid(row=1, column=0, padx=10, pady=10)

entry_folder = tk.Entry(root, width=50)
entry_folder.grid(row=1, column=1, padx=10, pady=10)

button_folder = tk.Button(root, text="Chọn thư mục", command=select_folder)
button_folder.grid(row=1, column=2, padx=10, pady=10)

button_start = tk.Button(root, text="Bắt đầu", command=start_processing)
button_start.grid(row=2, column=1, padx=10, pady=10)

# Thêm nhãn để hiển thị trạng thái
label_status = tk.Label(root, text="", fg="blue")
label_status.grid(row=3, column=1, padx=10, pady=10)

# Chạy vòng lặp giao diện
root.mainloop()

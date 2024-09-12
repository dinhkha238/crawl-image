import os
import time
import requests
from bs4 import BeautifulSoup
import spacy
import pytextrank
import tkinter as tk
from tkinter import filedialog, messagebox
from pytubefix import YouTube
from pytubefix.cli import on_progress
from threading import Thread

# Hàm tải ảnh từ URL
def download_image(url, file_name):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(file_name, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"Error: {response.status_code}")
            return False
    except Exception as e:
        print(f"Error")
        return False

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

    images = soup.find_all("a", {"class": "iusc"})
    img_urls = 0

    for image in images:
        m = image.get("m")
        if m:
            m = eval(m)
            img_url = m.get("murl")
            if img_url:
                timestamp = int(time.time() * 1000)
                save_path = os.path.join(folder_segment, f"{timestamp}.jpg")
                if download_image(img_url, save_path):
                    img_urls += 1
            if img_urls >= num_images:
                return

# Hàm tải ảnh với đa luồng
def process_images_threading(lines, folder_save, keyword_main):
    threads = []

    with open("log.txt", "a", encoding='utf-8') as log_file:
        for i, line in enumerate(lines):
            if i == 20:  # Giới hạn xử lý 20 từ khóa
                break
            keyword = get_keyword(line, keyword_main)
            len_text, first_character = count_characters_in_text(line)
            if len_text < 100:
                first_character = 1
            print(f"{i+1}. Keyword: {keyword}, Image number: {first_character}")
            
            # Ghi vào log.txt
            log_file.write(f"{i+1}. Keyword: {keyword}\n")
            log_file.write(f"Length: {len_text}, Image number: {first_character}\n\n")

            # Tạo một luồng cho mỗi lần gọi scrape_images
            thread = Thread(target=scrape_images, args=(keyword, i, folder_save, int(first_character)))
            threads.append(thread)
            thread.start()
            
    label_status_image.config(text="Xử lý thành công!", fg="green")
    

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
        # result = result + keyword_main 
    else:
        for phrase in doc._.phrases[:2]:
            if "Megan" in phrase.text:
                phrase.text = phrase.text.replace("Megan", "Meghan")
            result += phrase.text + ", "
    # Xóa dấu phẩy cuối cùng
    if result.endswith(", "):
        result = result[:-2]
    return result

def count_characters_in_text(text):
    stripped_line = text.strip()
    if stripped_line:  
        return len(stripped_line), str(len(stripped_line))[0]
    return 0, 0

# Hàm tải video từ YouTube
def download_video():
    video_url = entry_video.get()
    folder_save = entry_folder_video.get()

    if not video_url or not folder_save:
        messagebox.showerror("Lỗi", "Vui lòng nhập URL và chọn thư mục lưu!")
        return

    label_status_video.config(text="Đang tải video...", fg="blue")
    root.update()

    try:
        yt = YouTube(video_url, on_progress_callback=on_progress)
        ys = yt.streams.filter(file_extension='mp4', res='1080p').first()
        if not ys:
            ys = yt.streams.filter(file_extension='mp4', res='720p').first()
        if not ys:
            ys = yt.streams.filter(file_extension='mp4', res='480p').first()
        if not ys:
            ys = yt.streams.filter(file_extension='mp4', res='360p').first()

        if ys:
            ys.download(output_path=folder_save)
            label_status_video.config(text="Tải video thành công!", fg="green")
        else:
            label_status_video.config(text="Không tìm thấy video với định dạng mong muốn.", fg="red")

    except Exception as e:
        messagebox.showerror("Lỗi", f"Đã xảy ra lỗi: {e}")
        label_status_video.config(text="Tải video thất bại!", fg="red")

# Hàm xử lý ảnh từ từ khóa trong file văn bản
def start_processing():
    file_path = entry_file.get()
    folder_save = entry_folder_image.get()

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

    label_status_image.config(text="Đang xử lý...", fg="blue")
    root.update()
    keyword_main = get_keyword(lines[0])

    # Làm trống file log.txt trước khi ghi
    with open("log.txt", "w", encoding='utf-8') as log_file:
        log_file.write("")

    process_images_threading(lines, folder_save, keyword_main)

# Hàm tải ảnh từ từ khóa
def start_images_by_keyword():
    keyword = entry_keyword.get()
    folder_save = entry_folder_keyword.get()
    num_images = int(entry_number.get())

    if not keyword or not folder_save:
        messagebox.showerror("Lỗi", "Vui lòng nhập từ khóa và chọn thư mục lưu ảnh!")
        return

    label_status_keyword.config(text="Đang xử lý...", fg="blue")
    root.update()

    scrape_images(keyword, 0, folder_save, num_images)
    label_status_keyword.config(text="Xử lý thành công!", fg="green")

# Tạo giao diện chính
root = tk.Tk()
root.title("Ứng dụng Tải Ảnh & Video")

# Tạo khung cho tải ảnh
frame_image = tk.Frame(root)
frame_image.grid(row=0, column=0, padx=20, pady=20)

# Chọn file văn bản
label_file = tk.Label(frame_image, text="Chọn file văn bản (.txt):")
label_file.grid(row=0, column=0, padx=10, pady=10)

entry_file = tk.Entry(frame_image, width=50)
entry_file.grid(row=0, column=1, padx=10, pady=10)

button_file = tk.Button(frame_image, text="Chọn file", command=lambda: entry_file.insert(0, filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])))
button_file.grid(row=0, column=2, padx=10, pady=10)

# Chọn thư mục lưu ảnh
label_folder_image = tk.Label(frame_image, text="Chọn thư mục lưu ảnh:")
label_folder_image.grid(row=1, column=0, padx=10, pady=10)

entry_folder_image = tk.Entry(frame_image, width=50)
entry_folder_image.grid(row=1, column=1, padx=10, pady=10)

button_folder_image = tk.Button(frame_image, text="Chọn thư mục", command=lambda: entry_folder_image.insert(0, filedialog.askdirectory()))
button_folder_image.grid(row=1, column=2, padx=10, pady=10)

# Nút bắt đầu xử lý ảnh từ file
button_start_images = tk.Button(frame_image, text="Tải ảnh từ file", command=start_processing)
button_start_images.grid(row=2, column=1, padx=10, pady=10)

# Thêm nhãn hiển thị trạng thái ảnh
label_status_image = tk.Label(frame_image, text="", fg="blue")
label_status_image.grid(row=3, column=1, padx=10, pady=10)


# Tạo khung cho tải video
frame_video = tk.Frame(root)
frame_video.grid(row=0, column=1, padx=20, pady=20)

# Nhập URL video
label_video = tk.Label(frame_video, text="Nhập URL video YouTube:")
label_video.grid(row=0, column=0, padx=10, pady=10)

entry_video = tk.Entry(frame_video, width=50)
entry_video.grid(row=0, column=1, padx=10, pady=10)

# Chọn thư mục lưu video
label_folder_video = tk.Label(frame_video, text="Chọn thư mục lưu video:")
label_folder_video.grid(row=1, column=0, padx=10, pady=10)

entry_folder_video = tk.Entry(frame_video, width=50)
entry_folder_video.grid(row=1, column=1, padx=10, pady=10)

button_folder_video = tk.Button(frame_video, text="Chọn thư mục", command=lambda: entry_folder_video.insert(0, filedialog.askdirectory()))
button_folder_video.grid(row=1, column=2, padx=10, pady=10)

# Nút tải video
button_video = tk.Button(frame_video, text="Tải video", command=lambda: Thread(target=download_video).start())
button_video.grid(row=2, column=1, padx=10, pady=10)

# Thêm nhãn hiển thị trạng thái video
label_status_video = tk.Label(frame_video, text="", fg="blue")
label_status_video.grid(row=3, column=1, padx=10, pady=10)


# Tạo khung cho tải ảnh theo keyword
frame_keyword = tk.Frame(root)
frame_keyword.grid(row=1, column=0, columnspan=2, padx=20, pady=20)

# Nhập keyword
label_keyword = tk.Label(frame_keyword, text="Nhập từ khóa tìm kiếm ảnh:")
label_keyword.grid(row=0, column=0, padx=10, pady=10)

entry_keyword = tk.Entry(frame_keyword, width=50)
entry_keyword.grid(row=0, column=1, padx=10, pady=10)

# Nhập số lượng ảnh
label_number = tk.Label(frame_keyword, text="Số lượng ảnh:")
label_number.grid(row=1, column=0, padx=10, pady=10)

entry_number = tk.Entry(frame_keyword, width=10)
entry_number.grid(row=1, column=1, padx=10, pady=10, sticky='w')

# Chọn thư mục lưu ảnh
label_folder_keyword = tk.Label(frame_keyword, text="Chọn thư mục lưu ảnh:")
label_folder_keyword.grid(row=2, column=0, padx=10, pady=10)

entry_folder_keyword = tk.Entry(frame_keyword, width=50)
entry_folder_keyword.grid(row=2, column=1, padx=10, pady=10)

button_folder_keyword = tk.Button(frame_keyword, text="Chọn thư mục", command=lambda: entry_folder_keyword.insert(0, filedialog.askdirectory()))
button_folder_keyword.grid(row=2, column=2, padx=10, pady=10)

# Nút bắt đầu tìm và tải ảnh
button_start_keyword = tk.Button(frame_keyword, text="Tải ảnh theo keyword", command=lambda: Thread(target=start_images_by_keyword).start())
button_start_keyword.grid(row=3, column=1, padx=10, pady=10)

# Thêm nhãn hiển thị trạng thái tìm ảnh
label_status_keyword = tk.Label(frame_keyword, text="", fg="blue")
label_status_keyword.grid(row=4, column=1, padx=10, pady=10)

root.mainloop()

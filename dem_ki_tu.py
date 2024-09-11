def count_blank_lines(file_path):
    blank_line_count = 0
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip() != '':
                blank_line_count += 1
    return blank_line_count

# Ví dụ sử dụng
file_path = 'E.txt'
blank_lines = count_blank_lines(file_path)
print(f"Số lượng dòng trắng trong tệp là: {blank_lines}")

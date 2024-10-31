import os
import concurrent.futures

# Danh sách các tên thư mục cần thêm vào .gitignore
directory_names_to_ignore = ['logs', '__pycache__']

# Hàm kiểm tra và thêm thư mục vào .gitignore
def check_and_add_to_gitignore(directories):
    gitignore_path = '.gitignore'
    
    # Đọc nội dung của .gitignore chỉ một lần
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as file:
            current_ignored = set(file.read().splitlines())
    else:
        current_ignored = set()

    # Thêm các thư mục mới vào tập hợp
    added_directories = []
    for directory in directories:
        if directory not in current_ignored:
            current_ignored.add(directory)
            added_directories.append(directory)

    # Ghi lại các thay đổi vào .gitignore chỉ một lần
    if added_directories:
        with open(gitignore_path, 'w') as file:
            file.write('\n'.join(current_ignored) + '\n')

    return added_directories

# Hàm tìm kiếm các thư mục có tên logs hoặc __pycache__
def find_directories_to_ignore(root_dir):
    directories_found = []
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for dirname in dirnames:
            if dirname in directory_names_to_ignore:
                directories_found.append(os.path.relpath(os.path.join(dirpath, dirname), root_dir))
    
    return directories_found

def update_gitignore():
    # Lấy số lượng CPU trên máy
    num_cpus = os.cpu_count()
    print(f"Number of CPU cores: {num_cpus}")

    # Tìm các thư mục cần thêm vào .gitignore
    directories_to_ignore = find_directories_to_ignore('.')

    # Sử dụng ThreadPoolExecutor với số lượng worker bằng số CPU
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_cpus) as executor:
        # Gửi các nhiệm vụ kiểm tra và thêm thư mục vào gitignore
        future = executor.submit(check_and_add_to_gitignore, directories_to_ignore)

        # Xử lý kết quả
        added_directories = future.result()

    if added_directories:
        print(f"Added to .gitignore: {', '.join(added_directories)}")
    else:
        print("No new directories to add to .gitignore.")

if __name__ == "__main__":
    update_gitignore()

import logging
import os

def get_logger(name: str) -> logging.Logger:
    # Tạo thư mục logs nếu chưa tồn tại
    os.makedirs("logs", exist_ok=True)
    
    # Tạo logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Set mức log thấp nhất là DEBUG để ghi tất cả các log

    # Tạo formatter cho các log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Handler cho file logs/app.log (ghi tất cả các log)
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setLevel(logging.DEBUG)  # Ghi tất cả log vào app.log
    file_handler.setFormatter(formatter)

    # Handler cho file logs/error.log (chỉ ghi log mức ERROR trở lên)
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setLevel(logging.ERROR)  # Chỉ ghi log ERROR và CRITICAL vào error.log
    error_handler.setFormatter(formatter)

    # Thêm các handler vào logger
    if not logger.hasHandlers():  # Tránh thêm handler nhiều lần
        logger.addHandler(file_handler)
        logger.addHandler(error_handler)

    return logger

import pandas as pd

# Đọc file CSV
file_path = 'sales_pipeline.csv'
data = pd.read_csv(file_path)

# Thay thế 'GTXPro' bằng 'GTX Pro' trong cột 'product'
data['product'] = data['product'].replace('GTXPro', 'GTX Pro')

# Ghi lại file CSV đã sửa
data.to_csv(file_path, index=False)

print("Đã sửa xong file CSV.")

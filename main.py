"""Chạy toàn bộ pipeline ở đây"""

from etl.extract import extract_pg, setup_logging
from etl.load import load_bq

def main():
    setup_logging()
    data, schemas = extract_pg()
    print(f"Đã lấy {len(data)} bảng: {list(data.keys())}")
    load_bq(data, schemas)
    print("XONG")
if __name__ == "__main__":
    main()
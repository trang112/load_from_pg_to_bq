"""Trích xuất dữ liệu y nguyên từ Postgres:
    1. Trích xuất dữ liệu
    2. Trích xuất schemas các cột trong bảng
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

def setup_logging(level: str = "INFO", log_file:str = "main.log") -> None:
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
        handlers=[
            logging.FileHandler(log_file, mode="a", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

def extract_pg():
    """Trích xuất dữ liệu từ Postgres"""

    conn = psycopg2.connect(
            host=os.environ["SOURCE_DB_HOST"],
            port=os.environ["SOURCE_DB_PORT"],
            dbname=os.environ["SOURCE_DB_NAME"],
            user=os.environ["SOURCE_DB_USER"],
            password=os.environ["SOURCE_DB_PASSWORD"],
    )
    data = {}
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # BƯỚC 1: Câu lệnh SQL đặc biệt để lấy danh sách TÊN TẤT CẢ CÁC BẢNG do bạn tạo ra (schema 'public')
            cur.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
            """)
            all_tables = [row['table_name'] for row in cur.fetchall()]

            
            for table in all_tables:
                logger.info("Đang lấy dữ liệu từ bảng: %s...",table)
                cur.execute(f"SELECT * FROM {table}")
                rows = [dict(r) for r in cur.fetchall()]
                data[table] = rows
                logger.info("✅ Đã lấy xong %d dòng từ bảng %s.\n", len(rows),table)
                
            #Bước 2: câu lệnh SQL dùng để lấy schema của tất cả các cột trong các bảng:
            cur.execute("""
                SELECT table_name, column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position
            """)
            schemas = {}
            for r in cur.fetchall():
                logger.info("Đang lấy schemas từ bảng: %s...",r["table_name"])
                schemas.setdefault(r["table_name"], []).append(r)
                logger.info("Đã lấy xong schemas của %s cột",len(schemas[r["table_name"]]))

    finally:
        conn.close()
    return data, schemas



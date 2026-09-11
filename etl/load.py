"""Load nội dung đã lấy được từ Postgres lên Bigquer, giữ y nguyên không thay đổi"""

import json
import os
from google.cloud import bigquery
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

PG_TO_BQ = {
    "smallint": "INT64",
    "integer": "INT64",
    "bigint": "INT64",
    "real": "FLOAT64",
    "double precision": "FLOAT64",
    "numeric": "NUMERIC",
    "boolean": "BOOL",
    "character varying": "STRING",
    "character": "STRING",
    "text": "STRING",
    "uuid": "STRING",
    "date": "DATE",
    "timestamp without time zone": "DATETIME",
    "timestamp with time zone": "TIMESTAMP",
    "json": "JSON",
    "jsonb": "JSON",
}

def load_bq(data:dict, schemas:dict, write_disposition: str = "WRITE_TRUNCATE") -> None:
    """Load data vào Bigquery với schema giống với schema trên Postgres"""
    client = bigquery.Client()
    dataset = os.getenv("BQ_DATASET")

    for table_name, rows in data.items():
        bq_schema = []
        if table_name in schemas: #lấy schemas tương ứng với table đang xem
            for col in schemas[table_name]:
                col_name = col['column_name']
                bq_type = PG_TO_BQ.get(col['data_type'],"STRING") #lấy giá trị cột ở Bigquery 
                bq_schema.append(bigquery.SchemaField(col_name, bq_type, mode="NULLABLE"))
        
        # Thiết lập cấu hình Load Job với Schema cụ thể
        table_id = f"{client.project}.{dataset}.{table_name}"
        job_config = bigquery.LoadJobConfig(
            write_disposition= write_disposition,
            schema=bq_schema)
        
        payload = json.loads(json.dumps(rows, default=str))

        logger.info(f"Đang nạp {len(rows)} dòng vào bảng {table_id}...")
        job = client.load_table_from_json(payload, table_id, job_config=job_config)
        job.result()  # Chờ job hoàn thành
        
        logger.info(f"[load] Thành công: nạp {job.output_rows} dòng vào {table_id} {write_disposition}")




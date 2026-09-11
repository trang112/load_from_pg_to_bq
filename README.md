# BTVN 6 — Postgres → BigQuery ETL

Pipeline trích xuất toàn bộ bảng từ Postgres (`core_banking`) và nạp lên
BigQuery, giữ nguyên kiểu dữ liệu gốc.

## Cấu trúc

```
BTVN_6_PG_TO_BQ/
├── etl/
│   ├── __init__.py
│   ├── extract.py     # đọc bảng + schema từ Postgres
│   └── load.py        # dịch kiểu PG→BQ và nạp lên BigQuery
├── main.py            # entry point
├── test.ipynb         # notebook thử nghiệm
├── .env               # cấu hình (KHÔNG commit)
├── .env.example       # mẫu cấu hình
└── main.log           # log mỗi lần chạy
```

## Cách hoạt động

1. `extract_pg()` đọc `information_schema.tables` lấy danh sách bảng,
   `information_schema.columns` lấy kiểu dữ liệu từng cột,
    Trả về `(data, schemas)`.
2. `load_bq()` dịch kiểu Postgres sang kiểu BigQuery qua bảng map
   `PG_TO_BQ`, dựng `SchemaField` tường minh, rồi nạp bằng
   `load_table_from_json` với `WRITE_TRUNCATE`.

Dữ liệu đi qua RAM máy local, không ghi file trung gian.

## Bảng map kiểu

| Postgres | BigQuery |
|---|---|
| `integer`, `bigint`, `smallint` | `INT64` |
| `numeric` | `NUMERIC` |
| `double precision`, `real` | `FLOAT64` |
| `boolean` | `BOOL` |
| `character varying`, `text`, `uuid` | `STRING` |
| `date` | `DATE` |
| `timestamp without time zone` | `DATETIME` |
| `timestamp with time zone` | `TIMESTAMP` |
| `json`, `jsonb` | `JSON` |

Kiểu không có trong bảng sẽ thành `STRING`.

## Cài đặt

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env    # rồi điền giá trị thật
```

## Chạy

```bash
python main.py
```

## Kiểm tra kết quả

```bash
bq ls core_banking_bronze
bq show core_banking_bronze.transactions
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) FROM core_banking_bronze.customers'
```

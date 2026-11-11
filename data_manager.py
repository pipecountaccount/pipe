import csv
import json
import re
from pathlib import Path

# アプリのフォルダ内に保存領域を作成
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
IMAGES_DIR = OUTPUT_DIR / "images"
DATA_DIR = BASE_DIR / "data"
LOCATIONS_PATH = DATA_DIR / "locations.json"
CSV_PATH = OUTPUT_DIR / "combined.csv"

CSV_FIELDS = [
    "日時", "グループ", "場所", "AI検出数",
    "手動追加数", "最終合計", "備考", "画像ファイル名"
]

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
IMAGES_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)


def safe_filename_part(value, fallback):
    """ファイル名に使いにくい文字を置き換える"""
    value = str(value or "").strip()
    value = re.sub(r'[\\/:*?"<>|\\s]+', "_", value)
    value = value.strip("._")
    return value[:60] or fallback


def load_locations():
    """過去に入力した場所の一覧を読み込む"""
    if not LOCATIONS_PATH.exists():
        return []
    try:
        data = json.loads(LOCATIONS_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def add_location(location):
    """場所を重複させずに履歴へ追加する"""
    location = str(location or "").strip()
    if not location:
        return
    locations = load_locations()
    if location in locations:
        locations.remove(location)
    locations.insert(0, location)
    LOCATIONS_PATH.write_text(
        json.dumps(locations[:100], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def append_result(record):
    """1件の判定結果を統合CSVへ追記する"""
    file_exists = CSV_PATH.exists() and CSV_PATH.stat().st_size > 0
    with CSV_PATH.open("a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        if not file_exists:
            writer.writeheader()
        writer.writerow({field: record.get(field, "") for field in CSV_FIELDS})


def load_results():
    """統合CSVの全レコードを読み込む"""
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

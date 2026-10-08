import json
import urllib.request
import os
from datetime import datetime, timezone, timedelta

# ==========================
# 原作者源接口（固定）
# ==========================
SOURCE = "https://9280.kstore.vip/aiwex.json"
CONFIG_FILE = "config.json"
OUTPUT_FILE = "fish.json"

# ========== 关键字白名单：站点名称包含下面任意一个就保留 ==========
ALLOW_KEYWORDS = ["免费分享","秒播", "短剧", "漫剧", "漫短", "课堂", "音乐"]
# ======================================================

# ==========================
# 读取 JSON
# ==========================
def load_json(file):
    with open(
        file,
        "r",
        encoding="utf-8"
    ) as f:
        return json.load(f)

# ==========================
# 保存 JSON
# ==========================
def save_json(file, data):
    with open(
        file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2
        )

# ==========================
# 获取源接口
# ==========================
def fetch_source():
    print()
    print("====================")
    print("正在获取接口:")
    print(SOURCE)
    print("====================")
    req = urllib.request.Request(
        SOURCE,
        headers={
            "User-Agent":
            "Mozilla/5.0"
        }
    )
    try:
        with urllib.request.urlopen(
            req,
            timeout=30
        ) as response:
            text = response.read().decode(
                "utf-8-sig"
            )
            return json.loads(text)
    except Exception as e:
        raise Exception(
            f"接口获取失败: {e}"
        )

# ==========================
# 主程序
# ==========================
def main():
    start_time = datetime.now()
    cfg = {}
    if os.path.exists(CONFIG_FILE):
        cfg = load_json(CONFIG_FILE)
    rename = cfg.get("rename", {})

    data = fetch_source()
    source_sites = data.get("sites", [])
    if not source_sites:
        raise Exception("源接口没有 sites 数据")

    print()
    print("====================")
    print(f"开始按站点名称关键字过滤，允许关键字：{ALLOW_KEYWORDS}")
    print("====================")

    filtered_sites = []
    for site in source_sites:
        key = site.get("key")
        site_name = site.get("name", "")
        if not key or not site_name:
            continue
        # 判断站点名称是否包含任意一个允许关键字
        match = any(k in site_name for k in ALLOW_KEYWORDS)
        if not match:
            continue

        new_site = site.copy()
        if key in rename:
            new_site["name"] = rename[key]
        filtered_sites.append(new_site)

    if len(filtered_sites) == 0:
        raise Exception("没有匹配到任何站点，请检查关键字！")

    result = data.copy()
    result["sites"] = filtered_sites
    save_json(OUTPUT_FILE, result)

    # ==========================
    # UTC+8 时间
    # ==========================
    end_time = datetime.now(
        timezone(
            timedelta(hours=8)
        )
    )
    print()
    print("====================")
    print("生成完成")
    print("保留站点数量:", len(filtered_sites))
    print("耗时:", str(datetime.now() - start_time))
    print("时间:", end_time.strftime("%Y-%m-%d %H:%M:%S"))
    print("====================")
    for i, s in enumerate(filtered_sites, 1):
        name = s.get("name","")
        cat = s.get("类型") or s.get("type_name", "未知")
        print(f"{i:02d}. {name} [{s.get('key','')}] 【原分类:{cat}】")
    print("====================")
    print("输出文件:", OUTPUT_FILE)
    print("====================")

if __name__ == "__main__":
    main()

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

# ========== 【在这里配置允许保留的分类，按需修改】 ==========
ALLOW_CATEGORIES = ["秒播", "短剧", "漫剧", "教育", "音乐"]
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
    print(f"开始按分类过滤站点，允许分类：{ALLOW_CATEGORIES}")
    print("====================")

    filtered_sites = []
    for site in source_sites:
        key = site.get("key")
        if not key:
            continue
        # 读取站点分类字段，兼容两种常见字段名：类型 / type_name
        site_category = site.get("类型") or site.get("type_name", "")
        # 判断是否在允许分类列表
        if site_category not in ALLOW_CATEGORIES:
            continue

        # 保留该站点，处理重命名（你不需要重命名，rename为空就不生效）
        new_site = site.copy()
        if key in rename:
            new_site["name"] = rename[key]
        filtered_sites.append(new_site)

    if len(filtered_sites) == 0:
        raise Exception("没有匹配到任何站点，请检查分类名称是否和源接口一致！")

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
        cat = s.get("类型") or s.get("type_name", "未知分类")
        print(f"{i:02d}. {s.get('name','')} [{s.get('key','')}] 【分类:{cat}】")
    print("====================")
    print("输出文件:", OUTPUT_FILE)
    print("====================")

if __name__ == "__main__":
    main()

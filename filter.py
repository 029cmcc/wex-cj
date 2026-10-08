import json
import urllib.request
import os
from datetime import datetime, timezone, timedelta
# ==========================
# 原作者源接口（固定）
# ==========================
SOURCE = "https://9280.kstore.vip/aiwex.json"
OUTPUT_FILE = "fish.json"
# 筛选关键词，name包含其中任意一个就保留
KEYWORDS = ["免费分享","秒播", "短剧", "音乐", "课堂"]
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
    data = fetch_source()
    source_sites = data.get(
        "sites",
        []
    )
    if not source_sites:
        raise Exception(
            "源接口没有 sites 数据"
        )

    filtered_sites = []
    print()
    print("====================")
    print("按关键词过滤站点...")
    print(f"匹配关键词：{KEYWORDS}")
    print("====================")

    for site in source_sites:
        key = site.get("key","")
        name = site.get("name","")
        # 判断名称是否包含关键词
        match_kw = any(kw in name for kw in KEYWORDS)
        if match_kw:
            new_site = site.copy()
            # 单独处理Douban名称
            if key == "Douban":
                new_site["name"] = "🐮【免费分享】🐮"
            filtered_sites.append(new_site)

    if len(filtered_sites) == 0:
        raise Exception("没有匹配到任何站点，请检查关键词！")

    result = data.copy()
    result["sites"] = filtered_sites
    save_json(
        OUTPUT_FILE,
        result
    )
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
    print(
        "站点数量:",
        len(filtered_sites)
    )
    print(
        "耗时:",
        str(datetime.now() - start_time)
    )
    print(
        "时间:",
        end_time.strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )
    print("====================")
    for i, s in enumerate(
        filtered_sites,
        1
    ):
        print(
            f"{i:02d}. "
            f"{s.get('name','')}"
            f" [{s.get('key','')}]"
        )
    print("====================")
    print(
        "输出文件:",
        OUTPUT_FILE
    )
    print("====================")
if __name__ == "__main__":
    main()

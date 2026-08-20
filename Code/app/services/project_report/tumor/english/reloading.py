import re
from pathlib import Path

_IMAGE_EXTS = {".jpg", ".jpeg", ".png"}
_DASH_TABLE = str.maketrans({
    "\u2013": "-",  # en dash –
    "\u2014": "-",  # em dash —
    "\uff0d": "-",  # fullwidth －
    "_": "-",
})
_EXT_RE = re.compile(r"\.(?:jpg|jpeg|png)$", re.I)
_GROUP_RE = re.compile(r"G\s*(\d+)", re.I)
_SEP_DATE_RE = re.compile(
    r"(\d{4})\s*[.\-/年．。]\s*(\d{1,2})\s*[.\-/月．。]\s*(\d{1,2})\s*日?"
)
_COMPACT_DATE_RE = re.compile(r"(\d{4})(\d{2})(\d{2})")

def get_image_files(folder):
    """获取文件夹中的图片文件（jpg/jpeg/png）。"""
    folder_path = Path(folder)
    if not folder_path.exists():
        print(f"⚠️ 图片文件夹不存在: {folder}")
        return []
    return sorted(
        f for f in folder_path.iterdir()
        if f.is_file() and f.suffix.lower() in _IMAGE_EXTS
    )

def _normalize_stem(filename):
    stem = _EXT_RE.sub("", str(filename).strip())
    stem = stem.replace("\u3002", ".").replace("\uff0e", ".")
    stem = stem.translate(_DASH_TABLE)
    stem = re.sub(r"\s*-\s*", "-", stem)
    return re.sub(r"\s+", " ", stem).strip()

def _format_ymd(year, month, day):
    try:
        year, month, day = int(year), int(month), int(day)
    except (TypeError, ValueError):
        return None
    if not (1 <= month <= 12 and 1 <= day <= 31):
        return None
    return f"{year:04d}.{month:02d}.{day:02d}"

def _find_photo_date(date_raw):
    """从文件名剩余部分抠出日期，返回 (YYYY.MM.DD, match)。"""
    if not date_raw:
        return None, None
    sep = _SEP_DATE_RE.search(date_raw)
    if sep:
        formatted = _format_ymd(*sep.groups())
        if formatted:
            return formatted, sep
    compact = _COMPACT_DATE_RE.search(date_raw)
    if compact:
        formatted = _format_ymd(*compact.groups())
        if formatted:
            return formatted, compact
    return None, None

def extract_group_info(filename):
    """从文件名提取组、日期，以及把日期规范成 YYYY.MM.DD 后的显示名（保留鼠号）。"""
    stem = _normalize_stem(filename)
    group_match = _GROUP_RE.search(stem)
    if not group_match:
        return None, None, None
    group = f"G{int(group_match.group(1))}"
    remainder = stem[group_match.end():]
    formatted, match = _find_photo_date(remainder)
    caption = stem
    if formatted and match:
        start = group_match.end() + match.start()
        end = group_match.end() + match.end()
        caption = stem[:start] + formatted + stem[end:]
        caption = re.sub(r"\s*-\s*", "-", caption)
        caption = re.sub(r"\s+", " ", caption).strip()
    return group, formatted, caption

def chunk3(items):
    """把 items 每2个切成一行，不足补 None。"""
    for i in range(0, len(items), 2):
        chunk = items[i:i+2]
        if len(chunk) < 2:
            chunk.extend([None] * (2 - len(chunk)))
        yield chunk

def process_folder(folder):
    """处理文件夹中的图片，返回图片组数据列表"""
    #print(f"处理文件夹: {folder}")
    image_files = get_image_files(folder)
    #print(f"找到 {len(image_files)} 个图片文件")
    
    # 按组分类并构建上下文数据
    groups = {}
    for img_file in image_files:
        group, date, caption = extract_group_info(img_file.name)
        if group:
            if group not in groups:
                groups[group] = {
                    "group_label": f"Group-{group}",
                    "dates": [],
                    "items": []
                }
            
            # 收集所有日期
            if date and date not in groups[group]["dates"]:
                groups[group]["dates"].append(date)
            groups[group]["items"].append({
                "img": img_file.name,
                "name": caption or img_file.stem
            })
    
    # 构建图片组数据列表
    groups_list = []
    for group_data in groups.values():
        groups_list.append({
            "group_label": group_data["group_label"],
            "date": "，".join(group_data["dates"]),
            "rows": list(chunk3(group_data["items"]))
        })
    
    return groups_list

def process_images_for_docx(groups_list, base_folder, tpl):
    """处理图片组数据，将文件路径转换为InlineImage对象"""
    from docxtpl import InlineImage
    from docx.shared import Mm
    
    for group in groups_list:
        for row in group['rows']:
            for i, item in enumerate(row):
                if item:
                    img_path = Path(base_folder) / item['img']
                    row[i] = {
                        'img': InlineImage(tpl, str(img_path), width=Mm(80), height=Mm(58)),#宽高控制
                        'name': item['name']
                    }
    return groups_list

def get_image_context_for_docx(image_folder, doc_template):
    """获取可直接用于Word文档渲染的图片上下文数据"""
    # 处理图片文件夹，获取图片组数据列表
    groups_list = process_folder(image_folder)
    # 将图片文件路径转换为InlineImage对象
    processed_groups = process_images_for_docx(groups_list, image_folder, doc_template)
    return processed_groups

def process_image_data(image_folder, doc_template):
    """处理图片数据，返回可直接用于Word文档渲染的图片上下文数据"""
    # 获取处理后的图片组数据，包含InlineImage对象
    processed_groups = get_image_context_for_docx(image_folder, doc_template)
    
    return processed_groups

if __name__ == "__main__":
    # 直接使用默认参数执行
    folder = "mouse"  # 默认图片文件夹
    context = process_folder(folder)
    print("预处理完成，上下文数据已准备好")
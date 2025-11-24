from pathlib import Path

def get_image_files(folder):
    """获取文件夹中的所有图片文件"""
    folder_path = Path(folder)
    if not folder_path.exists():
        print(f"⚠️ 图片文件夹不存在: {folder}")
        return []
    
    return sorted([f for f in folder_path.glob("*.jpg") if f.is_file()])

def extract_group_info(filename):
    """从文件名提取组和日期信息"""
    parts = filename.split('-')
    if len(parts) >= 2:
        group = parts[0]  # G1
        date = parts[1]   # 20250901
        # 将日期格式化为 2025.09.01
        formatted_date = f"{date[:4]}.{date[4:6]}.{date[6:8]}"
        return group, formatted_date
    return None, None

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
        group, date = extract_group_info(img_file.name)
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
                "name": img_file.stem
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
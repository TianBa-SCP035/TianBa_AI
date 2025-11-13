# -*- coding: utf-8 -*-
import os, re
import logging
import warnings
from typing import Tuple, Dict, List, Optional
import cv2
import numpy as np
from paddleocr import PaddleOCR

# 关闭日志的打印
logging.disable(logging.DEBUG)  # 关闭DEBUG日志的打印
logging.disable(logging.WARNING)  # 关闭WARNING日志的打印
logging.disable(logging.INFO)  # 关闭INFO日志的打印

# 屏蔽所有类型的警告
warnings.simplefilter("ignore", category=Warning)
# 单独屏蔽特定类型的警告
warnings.filterwarnings("ignore", category=FutureWarning)  # 忽略所有 FutureWarning 类型的警告
warnings.filterwarnings("ignore", category=UserWarning)  # 忽略所有 UserWarning 类型的警告

# 固定输出目录
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ocr_out")
# 角度与阈值
ANGLES = (0, 90, 270)
MIN_SCORE = 0.20

# -------- 工具函数 --------
def imread_any(path: str, flags=cv2.IMREAD_COLOR) -> np.ndarray:
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Image not found: {path}")
    data = np.fromfile(path, dtype=np.uint8)
    img = cv2.imdecode(data, flags)
    if img is None:
        raise RuntimeError(f"cv2.imdecode failed: {path}")
    return img

def imwrite_any(path: str, bgr: np.ndarray) -> None:
    ok, buf = cv2.imencode(".png", bgr)
    if not ok:
        raise RuntimeError(f"imencode failed for: {path}")
    buf.tofile(path)

def rotate_90s(img: np.ndarray, angle: int) -> np.ndarray:
    a = angle % 360
    if a == 0:   return img
    if a == 90:  return np.rot90(img, 1).copy()
    if a == 180: return np.rot90(img, 2).copy()
    if a == 270: return np.rot90(img, 3).copy()
    raise ValueError("angle must be 0/90/180/270")

def poly_to_box(poly) -> Tuple[int,int,int,int]:
    # 处理不同类型的边界框数据
    if isinstance(poly, list) and all(isinstance(p, list) and len(p) >= 2 for p in poly):
        # 列表格式：[[x1,y1], [x2,y2], ...]
        xs = [p[0] for p in poly]; ys = [p[1] for p in poly]
    elif hasattr(poly, 'tolist'):
        # numpy数组，转换为列表
        poly_list = poly.tolist()
        if isinstance(poly_list[0], list) and len(poly_list[0]) >= 2:
            # 二维数组：[[x1,y1], [x2,y2], ...]
            xs = [p[0] for p in poly_list]; ys = [p[1] for p in poly_list]
        else:
            # 一维数组：[x1,y1,x2,y2,...]
            xs = poly_list[::2]; ys = poly_list[1::2]
    elif isinstance(poly, (list, tuple)) and len(poly) >= 4:
        # 一维列表或元组：[x1,y1,x2,y2,...]
        xs = poly[::2]; ys = poly[1::2]
    else:
        # 其他格式，尝试直接访问
        try:
            xs = [poly[0], poly[2]] if len(poly) >= 4 else [poly[0]]
            ys = [poly[1], poly[3]] if len(poly) >= 4 else [poly[1]]
        except (TypeError, IndexError):
            # 无法处理的格式，返回默认值
            return 0, 0, 0, 0
    
    return int(min(xs)), int(min(ys)), int(max(xs)), int(max(ys))

def norm_text(s: str) -> str:
    # 去掉空格/换行，统一符号
    return (str(s).replace("（","(").replace("）",")")
                  .replace("－","-").replace("—","-").replace("–","-")
                  .replace(" ", "").replace("\n","").replace("\r","")
                  .strip())

# -------- 核心步骤 --------
def run_paddleocr_blocks(img_rgb: np.ndarray, ocr: PaddleOCR, min_score: float):
    # 直接使用predict方法获取结果
    result = ocr.predict(img_rgb)
    blocks = []
    
    # 处理PaddleOCR的结果
    if result and len(result) > 0:
        ocr_result = result[0]  # 获取第一个结果
        
        # 使用字典方式获取文本、边界框和置信度
        texts = ocr_result.get('rec_texts', ocr_result.get('texts', []))
        boxes = ocr_result.get('rec_boxes', ocr_result.get('boxes', []))
        scores = ocr_result.get('rec_scores', ocr_result.get('scores', []))
        
        # 确保文本、边界框和置信度的数量一致
        min_len = min(len(texts), len(boxes), len(scores))
        
        for i in range(min_len):
            text = texts[i]
            box = boxes[i]
            
            # 处理边界框数据
            if hasattr(box, 'tolist'):
                # 如果是numpy数组，转换为列表
                box = box.tolist()
            
            # 处理置信度数据
            try:
                if hasattr(scores[i], 'item'):
                    # 如果是numpy标量，使用item()方法
                    conf = float(scores[i].item())
                else:
                    # 直接转换
                    conf = float(scores[i])
            except Exception:
                conf = 0.9
            
            if conf < min_score:
                continue
                
            blocks.append((poly_to_box(box), norm_text(text), conf))
    
    blocks.sort(key=lambda b: (b[0][1], b[0][0]))
    return blocks




def match_by_concat(blocks) -> Dict[str, Tuple[str, Tuple[int,int,int]]]:
    # 直接拼接所有文本块，不剔除中文字
    pieces, owners = [], []
    for i, (_, txt, _) in enumerate(blocks):
        if not txt:
            continue
        # 不再替换O和o为0，因为模型一般不会识别错
        pieces.append(txt)
        owners.extend([i]*len(txt))
    big = "".join(pieces)
    got = {}
    
    # 为每个字段实现精确匹配
    # 证书编号格式1：一个字母+12个数字
    cert_pattern1 = r"[A-Za-z]\d{12}"
    cert_match1 = re.search(cert_pattern1, big)
    if cert_match1:
        cert_value = cert_match1.group(0)
        # 获取涉及的文本块索引
        a, b = cert_match1.span()
        idxs = sorted(set(owners[a:b]))
        if idxs:
            # 计算边界框
            x0=y0=10**9; x1=y1=-10**9
            for i in idxs:
                bx = blocks[i][0]
                x0=min(x0,bx[0]); y0=min(y0,bx[1]); x1=max(x1,bx[2]); y1=max(y1,bx[3])
            got["cert"] = (cert_value, (x0,y0,x1,y1))
    
    # 证书编号格式2：No.加18位数字
    cert_pattern2 = r"No\.\d{18}"
    cert_match2 = re.search(cert_pattern2, big)
    if cert_match2 and "cert" not in got:  # 只有当第一种格式未匹配到时才使用第二种格式
        cert_value = cert_match2.group(0)
        # 获取涉及的文本块索引
        a, b = cert_match2.span()
        idxs = sorted(set(owners[a:b]))
        if idxs:
            # 计算边界框
            x0=y0=10**9; x1=y1=-10**9
            for i in idxs:
                bx = blocks[i][0]
                x0=min(x0,bx[0]); y0=min(y0,bx[1]); x1=max(x1,bx[2]); y1=max(y1,bx[3])
            got["cert"] = (cert_value, (x0,y0,x1,y1))
    
    # 生产许可证：SCXK(省份)年份-编号
    prod_pattern = r"SCXK[(（][^)）]{1,6}[)）]"
    prod_match = re.search(prod_pattern, big)
    if prod_match:
        prod_end = prod_match.end()
        prod_value = prod_match.group(0)
        # 查找最近的年份编号
        year_pattern = r"20\d{2}[-－—–]?[0-9]{3,6}"
        for match in re.finditer(year_pattern, big[prod_end:]):
            year_value = match.group(0)
            full_value = f"{prod_value}{year_value}"
            # 计算位置和边界框
            a, b = prod_match.start(), prod_end + match.end()
            idxs = sorted(set(owners[a:b]))
            if idxs:
                x0=y0=10**9; x1=y1=-10**9
                for i in idxs:
                    bx = blocks[i][0]
                    x0=min(x0,bx[0]); y0=min(y0,bx[1]); x1=max(x1,bx[2]); y1=max(y1,bx[3])
                got["prod"] = (full_value, (x0,y0,x1,y1))
            break
    
    # 使用许可证：SYXK(省份)年份-编号
    use_pattern = r"SYXK[(（][^)）]{1,6}[)）]"
    use_match = re.search(use_pattern, big)
    if use_match:
        use_end = use_match.end()
        use_value = use_match.group(0)
        # 查找最近的年份编号
        year_pattern = r"20\d{2}[-－—–]?[0-9]{3,6}"
        for match in re.finditer(year_pattern, big[use_end:]):
            year_value = match.group(0)
            full_value = f"{use_value}{year_value}"
            # 计算位置和边界框
            a, b = use_match.start(), use_end + match.end()
            idxs = sorted(set(owners[a:b]))
            if idxs:
                x0=y0=10**9; x1=y1=-10**9
                for i in idxs:
                    bx = blocks[i][0]
                    x0=min(x0,bx[0]); y0=min(y0,bx[1]); x1=max(x1,bx[2]); y1=max(y1,bx[3])
                got["use"] = (full_value, (x0,y0,x1,y1))
            break
    
    return got

def save_result_txt(path_dir: str, angle: int, blocks, nums=None) -> None:
    p = os.path.join(path_dir, "result.txt")
    with open(p, "w", encoding="utf-8") as f:
        f.write(f"OCR angle: {angle}\n")
        
        # 添加OCR识别的文本内容
        f.write("\nOCR blocks:\n")
        for box, text, conf in blocks:
            f.write(f"  Text: {text}, Confidence: {conf:.2f}\n")
        
        # 添加匹配结果
        if nums:
            f.write("\nMatch results:\n")
            for kind in ("cert", "prod", "use"):
                if kind in nums:
                    val, _ = nums[kind]
                    f.write(f"  {kind}: {val}\n")



# -------- 主函数 --------
def ocr_numbers(image_path: str) -> Dict[str, Dict[str, Optional[str]]]:
    """
    输入图片；在 OUT_DIR/<图片名>/ 落盘 result.txt；返回编号值
    """
    assert os.path.isfile(image_path), f"file not found: {image_path}"
    os.makedirs(OUT_DIR, exist_ok=True)
    base = os.path.splitext(os.path.basename(image_path))[0]
    out_dir = os.path.join(OUT_DIR, base)
    os.makedirs(out_dir, exist_ok=True)

    img_bgr0 = imread_any(image_path, cv2.IMREAD_COLOR)
    img_rgb0 = cv2.cvtColor(img_bgr0, cv2.COLOR_BGR2RGB)
    # 实例化OCR（使用快速移动版模型）
    ocr = PaddleOCR(use_textline_orientation=False, 
                    text_recognition_model_name="PP-OCRv4_mobile_rec", 
                    text_detection_model_name="PP-OCRv5_mobile_det")

    chosen = None
    for ang in ANGLES:
        img_rgb = rotate_90s(img_rgb0, ang)
        blocks = run_paddleocr_blocks(img_rgb, ocr, MIN_SCORE)
        # 直接使用拼接匹配，不再逐块匹配
        best = match_by_concat(blocks)
        chosen = (ang, img_rgb, blocks, best)
        if best:  # 有结果即停
            break

    ang, img_rgb, blocks, nums = chosen
    save_result_txt(out_dir, ang, blocks, nums)

    result = {
        "prod": {"value": None},
        "use" : {"value": None},
        "cert": {"value": None},
        "angle": ang,
        "out_folder": out_dir,
    }
    for kind in ("prod", "use", "cert"):
        if kind in nums:
            val, _ = nums[kind]
            result[kind]["value"] = val

    return result

# -------- 示例 --------
if __name__ == "__main__":
    # 使用相对路径避免中文路径问题
    img_path = r"D:\项目\李博自动化\二号堆\TNT_png\24G139201-20250225-B202502240761.png"
    out = ocr_numbers(img_path)
    print(out)
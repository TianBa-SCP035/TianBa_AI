import fitz
import cv2
import numpy as np
import os

DEFAULT_DIR = os.path.join(os.path.dirname(__file__), "tnt_png")

def process_pdf(pdf_path, save_path=None):
    if save_path is None:
        os.makedirs(DEFAULT_DIR, exist_ok=True)
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        save_path = os.path.join(DEFAULT_DIR, base_name + ".png")

    pix = fitz.open(pdf_path)[0].get_pixmap(dpi=300)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n).copy()
    if img.shape[2] == 4:  # 去掉 alpha 通道
        img = img[:, :, :3]
    # —— 红章检测并抹白 —— #
    lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
    _, a, b = cv2.split(lab)

    k = 1.0
    a_thr = float(a.mean()) + k * float(a.std())
    b_thr = float(b.mean()) - 0.2 * float(b.std())
    mask_a = (a.astype(np.float32) > a_thr)
    mask_b = (b.astype(np.float32) > b_thr)
    mask = (mask_a & mask_b).astype(np.uint8) * 255

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    mask_filled = np.zeros_like(mask)
    cv2.drawContours(mask_filled, cnts, -1, 255, thickness=cv2.FILLED)
    out = img.copy()
    out[mask_filled > 0] = (255, 255, 255)

    # —— 全局二值化（Otsu）—— #
    gray = cv2.cvtColor(out, cv2.COLOR_RGB2GRAY)
    _, bin_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # —— 膨胀腐蚀：先反转 → 形态学 → 再反转 —— #
    bin_inv = cv2.bitwise_not(bin_otsu)
    kernel_bin = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    bin_proc = cv2.morphologyEx(bin_inv, cv2.MORPH_OPEN, kernel_bin, iterations=0)
    bin_proc = cv2.morphologyEx(bin_proc, cv2.MORPH_CLOSE, kernel_bin, iterations=0)
    bin_final = cv2.bitwise_not(bin_proc)
    ok = cv2.imwrite(save_path, bin_final)
    if not ok:  # OpenCV 在中文/特殊路径可能写不进去
        _, buf = cv2.imencode(".png", bin_final)
        buf.tofile(save_path)
    return save_path

if __name__ == "__main__":
    pdf_path = r"D:\项目\李博自动化\二号堆\24G139201-20250225-B202502240761.pdf"
    out_path = process_pdf(pdf_path)
    print(f"结果已保存到: {out_path}")

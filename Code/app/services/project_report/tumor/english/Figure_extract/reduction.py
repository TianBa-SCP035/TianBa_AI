import os
from PIL import Image
import threading

def compress_image(file_path):
    """压缩单个图片文件，分辨率改为原来的三分之一"""
    try:
        with Image.open(file_path) as img:
            if img.mode == 'RGBA':
                img = img.convert('RGB')
            
            width, height = img.size
            new_size = (width // 3, height // 3)
            img = img.resize(new_size, Image.Resampling.NEAREST)
            img.save(file_path, format='JPEG', quality=50, optimize=False)
    except:
        pass

def compress_images_in_folder(folder_path):
    """压缩指定文件夹内的所有图片，缩小分辨率并压缩"""
    if not os.path.exists(folder_path):
        return

    threads = []
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
            file_path = os.path.join(folder_path, filename)
            thread = threading.Thread(target=compress_image, args=(file_path,))
            threads.append(thread)
            thread.start()
    
    for thread in threads:
        thread.join()

def compress_experiment_images(experiment_id, photo_dir):
    """压缩指定实验编号文件夹中的图片"""
    experiment_dir = os.path.join(photo_dir, experiment_id)
    
    mouse_dir = os.path.join(experiment_dir, "mouse")
    tumor_dir = os.path.join(experiment_dir, "tumor")
    
    compress_images_in_folder(mouse_dir)
    compress_images_in_folder(tumor_dir)
    print("✅ 图片压缩完成！")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        experiment_id = sys.argv[1]
        compress_experiment_images(experiment_id)
    else:
        compress_images_in_folder("mouse")
        compress_images_in_folder("tumor")
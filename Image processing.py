import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from sklearn.cluster import KMeans
import os

# Глобальные переменные
result_image = None
segmented_image = None
method = None
theme = "light"
buttons = []

# Чтение изображений c русскими ссылками
def unicode(image_path):
    stream = np.fromfile(image_path, dtype=np.uint8)
    return cv2.imdecode(stream, cv2.IMREAD_COLOR)

def unicode_grayscale(image_path):
    stream = np.fromfile(image_path, dtype=np.uint8)
    return cv2.imdecode(stream, cv2.IMREAD_GRAYSCALE)

#Облако точек
def point_cloud(image_path):
    image_bgr = unicode(image_path)
    if image_bgr is None:
        raise ValueError("Не удалось загрузить изображение.")
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    #Преобразование LAB
    image_lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2Lab)
    l, a, b = cv2.split(image_lab)
    #Преобразование CLASHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_clahe = clahe.apply(l)
    image_rgb_clahe = cv2.cvtColor(cv2.merge((l_clahe, a, b)), cv2.COLOR_Lab2RGB)
    #Преобразование в градации серого
    image_gray = cv2.cvtColor(image_rgb_clahe, cv2.COLOR_RGB2GRAY)
    #Алгоритм Сanny поиска границ
    edges = cv2.Canny(image_gray, 70, 250)
    #Поиск контуров
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours, image_rgb

#Раскраска
def coloring(image_path, num_colors=5):
    image_bgr = unicode(image_path)
    if image_bgr is None:
        raise ValueError("Не удалось загрузить изображение.")
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    #Преобразование LAB
    image_lab = cv2.cvtColor(image_rgb, cv2.COLOR_RGB2Lab)
    l, a, b = cv2.split(image_lab)
    #Преобразование CLASHE
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_clahe = clahe.apply(l)
    image_clahe = cv2.cvtColor(cv2.merge((l_clahe, a, b)), cv2.COLOR_Lab2RGB)
    image_2d = image_clahe.reshape((-1, 3))
    #Преобразование KMEANS
    kmeans = KMeans(n_clusters=num_colors, random_state=42, n_init=10)
    kmeans.fit(image_2d)
    #Сегментируем изображение
    segmented_image = kmeans.cluster_centers_[kmeans.labels_].reshape(image_rgb.shape).astype(np.uint8)
    #Преобразование в серое
    image_gray = cv2.cvtColor(segmented_image, cv2.COLOR_RGB2GRAY)
    #Алгоритм Canny
    edges = cv2.Canny(image_gray, 50, 150)
    #Поиск контуров
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours, image_rgb, segmented_image

#SHIFT
def SHIFT(image_path):
    image = unicode_grayscale(image_path)
    if image is None:
        raise ValueError("Изображение не найдено или указан неверный путь")
    sift = cv2.SIFT_create()
    keypoints, descriptors = sift.detectAndCompute(image, None)
    return image, keypoints, descriptors

#Сравнение ключевых точек 
def ransac(image1_path, image2_path, ratio=0.75):
#Ключевые точки 1 изображения
    image1, keypoints1, descriptors1 = SHIFT(image1_path)
#Ключевые точки 2 изображения
    image2, keypoints2, descriptors2 = SHIFT(image2_path)
    bf = cv2.BFMatcher(cv2.NORM_L2)
#Алгорим Ransac для сопоставления ключевых точек
    matches = bf.knnMatch(descriptors1, descriptors2, k=2)
    good_matches = [m for m, n in matches if m.distance < ratio * n.distance]
    src_pts = np.float32([keypoints1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([keypoints2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    matches_mask = mask.ravel().tolist()
    return cv2.drawMatches(image1, keypoints1, image2, keypoints2, good_matches, None,
                           matchColor=(0, 255, 0), matchesMask=matches_mask,
                           flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)

# Ключевые точки методом SHIFT
def image_method_SHIFT(image_path):
    image_bgr = unicode(image_path)
    if image_bgr is None:
        raise ValueError("Не удалось загрузить изображение.")
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
#Поиск ключевых точек
    sift = cv2.SIFT_create()
    keypoints, _ = sift.detectAndCompute(image_rgb, None)
    image_with_keypoints = image_rgb.copy()
    np.random.seed(42)
    for kp in keypoints:
        x, y = int(kp.pt[0]), int(kp.pt[1])
        color = tuple(np.random.randint(0, 256, 3).tolist())
        cv2.circle(image_with_keypoints, (x, y), 7, color, -1)
    return image_with_keypoints

#Рисуем точки
def draw_contours(base_image, contours, point_size=3, step=10):
    white_background = np.ones_like(base_image) * 255
    for contour in contours:
        for i, point in enumerate(contour):
            if i % step == 0:
                cv2.circle(white_background, tuple(point[0]), point_size, (0, 0, 0), -1)
    return white_background

#Рисуем контуры
def color_contours(base_image, contours):
    white_background = np.ones_like(base_image) * 255
    for contour in contours:
        mask = np.zeros(base_image.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, cv2.FILLED)
        mean_color = tuple(map(int, cv2.mean(base_image, mask=mask)[:3]))
        cv2.drawContours(white_background, [contour], -1, mean_color, thickness=3)
    return white_background

#Выбор метода
def display(method):
    global result_image, segmented_image, current_method
    if method in [1, 2, 4]:
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        try:
            current_method = method
            if method == 1:
                contours, base_image = point_cloud(file_path)
                result_image = draw_contours(base_image, contours)
                segmented_image = None
            elif method == 2:
                contours, base_image, segmented_image = coloring(file_path)
                result_image = color_contours(base_image, contours)
                segmented_image = segmented_image
            elif method == 4:
                result_image = image_method_SHIFT(file_path)
                segmented_image = None
            display_image(result_image)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    elif method == 3:
        image1_path = filedialog.askopenfilename(title="Выберите первое изображение")
        image2_path = filedialog.askopenfilename(title="Выберите второе изображение")
        if not image1_path or not image2_path:
            return
        try:
            result_image = ransac(image1_path, image2_path)
            segmented_image = None
            display_image(result_image)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

#Сохранение результата
def save_result():
    if result_image is None:
        messagebox.showwarning("Нет изображения", "Сначала обработайте изображение.")
        return
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG", "*.png")])
    if not file_path:
        return
    success, encoded_image = cv2.imencode('.png', cv2.cvtColor(result_image, cv2.COLOR_RGB2BGR))
    if success:
        encoded_image.tofile(file_path)
        messagebox.showinfo("Сохранено", "Изображение успешно сохранено.")
    else:
        messagebox.showerror("Ошибка", "Ошибка при сохранении.")
#Вывод изображения
def display_image(image):
    max_width, max_height = 1200, 900
    height, width = image.shape[:2]
    scale = min(max_width / width, max_height / height)
    new_size = (int(width * scale), int(height * scale))
    image_resized = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    image_pil = Image.fromarray(image_resized)
    image_tk = ImageTk.PhotoImage(image_pil)
    label_image.config(image=image_tk)
    label_image.image = image_tk

#Смена темы
def toggle_theme():
    global theme
    theme = "dark" if theme == "light" else "light"
    apply_theme()

def apply_theme():
    style = ttk.Style()
    if theme == "dark":
        bg = "#2B2B2B"
        fg = "#FFFFFF"
        style.theme_use("clam")
        style.configure("TButton", background="#B94E48", foreground=fg, font=("Arial", 10, "bold"))
    else:
        bg = "#F7F7F7"
        fg = "#000000"
        style.theme_use("default")
        style.configure("TButton", background="#B94E48", foreground=fg, font=("Arial", 10))
    root.configure(bg=bg)
    label_image.configure(bg=bg)

def main():
    global root, label_image
    root = tk.Tk()
    root.title("Обработка изображений")
    root.geometry("1000x700")

    frame_buttons = ttk.Frame(root)
    frame_buttons.pack(pady=10)

#Кнопки
    button_data = [
        ("Метод 1: Облако точек", 1),
        ("Метод 2: Раскраска", 2),
        ("Метод 3: Сопоставление", 3),
        ("Метод 4: Shift", 4),
        ("Сохранить", "save"),
        ("Сменить тему", "theme")
    ]

    for text, cmd in button_data:
        action = lambda m=cmd: save_result() if m == "save" else toggle_theme() if m == "theme" else display(m)
        btn = ttk.Button(frame_buttons, text=text, command=action)
        btn.pack(side=tk.LEFT, padx=5)

    label_image = tk.Label(root, bg="white", relief=tk.SUNKEN, bd=2)
    label_image.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    apply_theme()
    root.mainloop()

if __name__ == "__main__":
    main()

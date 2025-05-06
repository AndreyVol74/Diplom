Функционал приложения 

Desktop по обработке изображения:

![image](https://github.com/user-attachments/assets/bbbe6023-3531-4dbb-9962-d9fbe28e7334)

    Функция def point_cloud(image_path):
Строит облако точек

![19](https://github.com/user-attachments/assets/44decbc1-5fad-4387-aadb-6a866a7b0026)    
![4](https://github.com/user-attachments/assets/67dd1f37-cac0-49a9-a1c9-d5f2d7b4ead3)

Раскраска

def coloring(image_path, num_colors=5):

![image](https://github.com/user-attachments/assets/2e6dbcc1-5308-41a8-b612-2cd06dce5c28)
![image](https://github.com/user-attachments/assets/0a4b7faf-6ac2-439e-9936-0ca888a32da9)

Сопостовления ключевых точек на двух изображениях

def ransac(image1_path, image2_path, ratio=0.75):

![image](https://github.com/user-attachments/assets/79e5e929-6a05-4828-9c81-acbe980f1b72)

Определение ключевых точек с помощью алгоритма Shift

def image_method_SHIFT(image_path):

![image](https://github.com/user-attachments/assets/1db687cb-40cf-4308-a7ad-77572af71ebe)

![image](https://github.com/user-attachments/assets/cd5edc82-7406-4cdd-a2f1-e2cf7577005d)

Расчет прямой кинематики робота манипулятора dofbot 

![image](https://github.com/user-attachments/assets/9a1074ba-109a-48a3-bbdc-b88e2fef014b)

Математические расчеты 

Сформировали JSON, скоординатами робота.

![image](https://github.com/user-attachments/assets/0e2c7af1-b37f-41ed-a735-955c69cae64f)

Построили прямую из 3 точек

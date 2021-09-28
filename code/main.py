import time
import PngDecoder as PD
start = time.perf_counter()
# 图片地址
Paddress1 = "C:\\Users\\裴俊博\\Desktop\\实习题-实现png解码器\\后端组实习题PngDecoder\\task3\\test1.png"

# 处理图片
PNGpicture = PD.PNG(Paddress1)
PNGpicture.changegray()
PNGpicture.createpng()
end = time.perf_counter()
print(end-start)

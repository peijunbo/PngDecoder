import PngDecoder as PD
# 图片地址
Paddress1 = "C:\\Users\\裴俊博\\Desktop\\实习题-实现png解码器\\后端组实习题PngDecoder\\task3\\test1.png"

# 处理图片
PNGpicture = PD.PNG(Paddress1)
outtxt = PNGpicture.getchpainting()
outfile = open('..\\docs\\test5.txt', 'w')
outfile.write(outtxt)
outfile.close()

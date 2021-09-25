import PngDecoder as PD
# 图片地址
Paddress1 = "C:\\Users\\裴俊博\\Desktop\\实习题-实现png解码器\\后端组实习题PngDecoder\\task3\\origin.png"

# 处理图片
PNGpicture = PD.PNG(Paddress1)

outtxt = PNGpicture.getchpainting(14)
outfile = open('..\\test\\test.txt', 'w')
outfile.write(outtxt)
outfile.close()

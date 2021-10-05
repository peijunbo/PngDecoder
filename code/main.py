import PngDecoder as pd
pngpath = "C:\\Users\\裴俊博\\Desktop\\实习题-实现png解码器\\后端组实习题PngDecoder\\task3\\test2.png"
png = pd.PNG(pngpath)
for i in png.cklist:
    print(i.Type, i.Length, i.CRC)
png.changeedge()
png.createpng()


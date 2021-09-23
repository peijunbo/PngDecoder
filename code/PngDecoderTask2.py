import struct



#创建数据块类每个类变量内有该数据块的信息
class chunk:
    def __init__(self, index, list):
        self.Length = list[index]*(16**6) + list[index+1]*(16**4) + list[index + 2]*(16**2) + list[index + 3]
        index += 4
        self.Type = chr(list[index]) + chr(list[index+1]) + chr(list[index+2]) + chr(list[index+3])
        index += 4

        #处理数据块
        self.Dataindex = index
        index += self.Length
        #CRC
        self.CRC = [list[index], list[index+1], list[index+2], list[index+3]]
        self.endindex = index + 4
    def IHDRwidth(self, list):
        if self.Type == "IHDR":
            Width = list[self.Dataindex]*(16**6) + list[self.Dataindex+1]*(16**4) + list[self.Dataindex + 2]*(16**2) + list[self.Dataindex + 3]
            return Width
    def IHDRHeight(self, list):
        if self.Type == "IHDR":
            Height = list[self.Dataindex+4]*(16**6) + list[self.Dataindex+5]*(16**4) + list[self.Dataindex + 6]*(16**2) + list[self.Dataindex + 7]
            return Height
    def IHDRBitDepth(self, list):
        if self.Type == "IHDR":
            BitDepth = list[self.Dataindex + 8]
            return BitDepth
    def IHDRColorType(self, list):
        if self.Type == "IHDR":
            ColorType = list[self.Dataindex + 9]
            return ColorType
    def IHDRComMethod(self, list):
        if self.Type == "IHDR":
            ComMethod = list[self.Dataindex + 10]
            return ComMethod
    def IHDRFilMethod(self, list):
        if self.Type == "IHDR":
            FilMethod = list[self.Dataindex + 11]
            return FilMethod
    def IHDRIntMethod(self, list):
        if self.Type == "IHDR":
            IntMethod = list[self.Dataindex + 12]
            return IntMethod
#定义一个将各个数据块存入列表的函数
def setchunk(list, index = 8):
    outlist = []
    while index < len(list):
        ck = chunk(index, list)
        outlist.append(ck)
        index = ck.endindex
    return outlist

class PNG:
    def __init__(self, pfile):
        pfile = pfile.read()
        pfile = struct.unpack(str(len(pfile)) + "c", pfile)
        # 建一个记录的列表
        self.list = []
        for i in pfile:
            a = i.hex()
            a = int(a, 16)
            self.list.append(a)
        del a
        self.cklist = setchunk(self.list)
        #处理自身的IHDR
        self.IHDR = self.cklist[0]
    def doIHDR(self):
        self.Width = self.IHDR.IHDRwidth(self.list)
        self.Height = self.IHDR.IHDRHeight(self.list)
        self.BitDepth = self.IHDR.IHDRBitDepth(self.list)
        self.ColorType = self.IHDR.IHDRColorType(self.list)
        self.ComMethod = self.IHDR.IHDRComMethod(self.list)
        self.FilMethod = self.IHDR.IHDRFilMethod(self.list)
        self.IntMethod = self.IHDR.IHDRIntMethod(self.list)

#图片地址
Paddress1 = "C:\\Users\裴俊博\Desktop\实习题-实现png解码器\后端组实习题PngDecoder\\task2\\test3.png"

#输出的文件地址
txtaddress1 = "..\\docs\\test3.txt"
#txtaddress1 = "test3.txt"
picture1 = open(Paddress1, mode = "rb")

#处理图片
PNGpicture = PNG(picture1)
PNGpicture.doIHDR()

#写入文件
shuchu = open(txtaddress1, mode="w")
shuchu.write("Width = " + str(PNGpicture.Width) + "\n")
shuchu.write("Height = " + str(PNGpicture.Height) + "\n")
shuchu.write("BitDepth = " + str(PNGpicture.BitDepth) + "\n")
shuchu.write("ColorType = " + str(PNGpicture.ColorType) + "\n")
shuchu.write("ComMethod = " + str(PNGpicture.ComMethod) + "\n")
shuchu.write("FilMethod = " + str(PNGpicture.FilMethod) + "\n")
shuchu.write("IntMethod = " + str(PNGpicture.IntMethod) + "\n")




picture1.close()
shuchu.close()

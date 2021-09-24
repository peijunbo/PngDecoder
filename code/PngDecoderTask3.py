import struct
import zlib


# 创建数据块类每个类变量内有该数据块的信息
class Chunk:
    def __init__(self, index, list):
        self.Length = list[index]*(16**6) + list[index+1]*(16**4) + list[index + 2]*(16**2) + list[index + 3]
        index += 4
        self.Type = chr(list[index]) + chr(list[index+1]) + chr(list[index+2]) + chr(list[index+3])
        index += 4

        # 处理数据块
        self.Dataindex = index

        self.Data = list[index:index+self.Length]
        index += self.Length
        # CRC
        self.CRC = [list[index], list[index+1], list[index+2], list[index+3]]
        self.endindex = index + 4

    def IHDRWidth(self, list):
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


# 定义一个将各个数据块存入列表的函数
def setchunk(ls, index = 8):
    outlist = []
    while index < len(ls):
        ck = Chunk(index, ls)
        outlist.append(ck)
        index = ck.endindex
    return outlist


class PNG:
    def __init__(self, pfile):
        pfile = pfile.read()
        pfile = struct.unpack(str(len(pfile)) + "c", pfile)
        self.oringinlist = pfile
        # 建一个记录的列表
        self.intlist = []
        for i in pfile:
            a = i.hex()
            a = int(a, 16)
            self.intlist.append(a)
        self.cklist = setchunk(self.intlist)
        # 处理自身的IHDR
        self.IHDR = self.cklist[0]

    def doihdr(self):
        self.Width = self.IHDR.IHDRWidth(self.intlist)
        self.Height = self.IHDR.IHDRHeight(self.intlist)
        self.BitDepth = self.IHDR.IHDRBitDepth(self.intlist)
        self.ColorType = self.IHDR.IHDRColorType(self.intlist)
        self.ComMethod = self.IHDR.IHDRComMethod(self.intlist)
        self.FilMethod = self.IHDR.IHDRFilMethod(self.intlist)
        self.IntMethod = self.IHDR.IHDRIntMethod(self.intlist)

    def packidat(self):
        outlist = []
        for i in self.cklist:
            if i.Type == "IDAT":
                outlist.extend(self.oringinlist[i.Dataindex:i.Dataindex+i.Length])
        return outlist

    def xy_to_rgbindex(self, x, y):
        if x == 0:
            index = y
        else:
            index = x*self.Width+y
        return index


# 图片地址
Paddress1 = "C:\\Users\\裴俊博\\Desktop\\实习题-实现png解码器\\后端组实习题PngDecoder\\task3\\origin.png"
# 输出的文件地址
txtaddress1 = "..\\docs\\test3.txt"
# txtaddress1 = "test4.txt"
# 处理图片
picture1 = open(Paddress1, mode = "rb")
PNGpicture = PNG(picture1)
PNGpicture.doihdr()
compress = PNGpicture.packidat()
compress = struct.pack(str(len(compress))+"c",*compress)
decompress = zlib.decompress(compress)
decompress = struct.unpack(str(len(decompress))+"c", decompress)


delist = []
fillist = []

for i in decompress:
    delist.append(i)

for i in range(PNGpicture.Height):
    a = delist.pop(i*PNGpicture.Width*3)
    a = a.hex()
    a = int(a, 16)
    fillist.append(a)
# 建立rgb列表
rlist = []
glist = []
blist = []
rgblist = []
for i in delist:
    rgblist.append(int(i.hex(), 16))
for i in range(len(rgblist)):
    a= rgblist[i]
    if i % 3 == 0:
        rlist.append(a)
    elif i % 3 == 1:
        glist.append(a)
    else:
        blist.append(a)


# 分行计算
def getrgb(picture, rgblist, filter):
    for i in range(picture.Height):
        if filter[i] == 0:
            continue
        elif filter[i] == 1:
            for j in range(picture.Width - 1):
                a = rgblist[j + i * picture.Width]
                rgblist[j + 1 + i * picture.Width] = (a + rgblist[j + 1 + i * picture.Width]) % 256
        elif filter[i] == 2:
            for j in range(picture.Width):
                b = rgblist[j + (i-1) * picture.Width]
                rgblist[j + i * picture.Width] = (b + rgblist[j + i * picture.Width]) % 256
        elif filter[i] == 3:
            for j in range(picture.Width):
                if j == 0:
                    b = rgblist[(i - 1) * picture.Width]
                    rgblist[i * picture.Width] = (b//2 + rgblist[i * picture.Width]) % 256
                else:
                    a = rgblist[j - 1 + i * picture.Width]
                    b = rgblist[j + (i - 1) * picture.Width]
                    rgblist[j + i * picture.Width] = ((a+b)//2 + rgblist[j + i * picture.Width]) % 256
        elif filter[i] == 4:
            for j in range(picture.Width):
                if j == 0:
                    a = 0
                    b = rgblist[j + (i - 1) * picture.Width]
                    c = 0
                    p = a + b - c
                    pa = abs(p - a)
                    pb = abs(p - b)
                    pc = abs(p - c)
                    if pa <= pb and pa <= pc:
                        ret = a
                    elif pb <= pc:
                        ret = b
                    else:
                        ret = c
                    rgblist[j + i * picture.Width] = (rgblist[j + i * picture.Width] + ret) % 256
                else:
                    a = rgblist[j - 1 + i * picture.Width]
                    b = rgblist[j + (i - 1) * picture.Width]
                    c = rgblist[j - 1 + (i - 1) * picture.Width]
                    p = a + b - c
                    pa = abs(p - a)
                    pb = abs(p - b)
                    pc = abs(p - c)
                    if pa <= pb and pa <= pc:
                        ret = a
                    elif pb <= pc:
                        ret = b
                    else:
                        ret = c
                    rgblist[j + i * picture.Width] = (rgblist[j + i * picture.Width] + ret) % 256
    return rgblist


rlist = getrgb(PNGpicture, rlist, fillist)
glist = getrgb(PNGpicture, glist, fillist)
blist = getrgb(PNGpicture, blist, fillist)
# 将结果写入文件
shuchu = open(txtaddress1, "w")
for x in range(PNGpicture.Height):
    for y in range(PNGpicture.Width):
        ind = PNGpicture.xy_to_rgbindex(x, y)
        text = "("+str(x)+","+str(y)+","+str(rlist[ind])+","+str(glist[ind])+","+str(blist[ind])+")"
        shuchu.write(text)
picture1.close()
shuchu.close()

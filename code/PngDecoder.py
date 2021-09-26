import struct
import zlib

# 创建数据块类每个类变量内有该数据块的信息
class Chunk:
    def __init__(self, index, bytesls, list):
        self.bLength = bytesls[index:index+4]
        self.Length = list[index]*(16**6) + list[index+1]*(16**4) + list[index + 2]*(16**2) + list[index + 3]
        index += 4
        self.bType = bytesls[index:index + 4]
        self.Type = chr(list[index]) + chr(list[index+1]) + chr(list[index+2]) + chr(list[index+3])
        index += 4

        # 处理数据块
        self.Dataindex = index

        self.Data = list[index:index+self.Length]
        self.bData = bytesls[index:index+self.Length]
        index += self.Length
        # CRC
        self.bCRC = bytesls[index:index + 4]
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

    def reidat(self):
        for i in range(len(self.Data)):
            self.Data[i] = bytes_to_int(self.bData[i])


# 将bytes变为int
def bytes_to_int(bytes):
    a = [1, 2]

    if type(bytes) == type(a):
        outnum = []
        for i in bytes:
            outnum.append(int(i.hex(), 16))
    else:
        outnum = int(bytes.hex(), 16)
    return outnum

# 定义一个将各个数据块存入列表的函数
def setchunk(ls, originls, index=8):
    outlist = []
    while index < len(ls):
        ck = Chunk(index, originls, list=ls)
        outlist.append(ck)
        index = ck.endindex
    return outlist

def createidat(idatlist):
    outlist = []
    crclist = [0, 0, 0, 0]
    for i in range(len(crclist)):
        a = crclist[i]
        crclist[i] = a.to_bytes(1, "big", signed=False)
    while len(idatlist) > 2**31-1:
        chunk = []
        # Length
        lengthlist = [255, 255, 255, 255]
        for i in range(len(lengthlist)):
            lengthlist[i] = lengthlist[i].to_bytes(1, "big", signed=False)
        chunk.extend(lengthlist)
        # Type
        typelist = [73, 68, 65, 84]
        for i in range(len(typelist)):
            typelist[i] = typelist[i].to_bytes(1, "big", signed=False)
        chunk.extend(typelist)
        # Data
        chunk.extend(idatlist[:2**31-1])
        # CRC
        chunk.extend(crclist)
        intchunk = bytes_to_int(chunk)
        outlist.append(Chunk(0, chunk, intchunk))
        del idatlist[:2**31-1]
    chunk = []
    # Length
    length = len(idatlist).to_bytes(4, "big", signed=False)
    length = struct.unpack("4c", length)
    chunk.extend(length)
    # type
    typelist = [73, 68, 65, 84]
    for i in range(len(typelist)):
        typelist[i] = typelist[i].to_bytes(1, "big", signed=False)
    chunk.extend(typelist)
    # Data
    chunk.extend(idatlist)
    # CRC
    chunk.extend(crclist)
    intchunk = bytes_to_int(chunk)
    outlist.append(Chunk(0, chunk, intchunk))
    outlist.reverse()
    return outlist


class PNG:
    def __init__(self, padress):
        pfile = open(padress, mode='rb')
        originbytes = pfile.read()
        pfile.close()
        self.byteslist = struct.unpack(str(len(originbytes))+"c", originbytes)

        self.pnghead = self.byteslist[:8]
        # 建一个记录的列表
        self.intlist = []
        for i in self.byteslist:
            a = bytes_to_int(i)
            self.intlist.append(a)
        self.cklist = setchunk(self.intlist, self.byteslist)



        # 处理自身的IHDR
        self.IHDR = self.cklist[0]
        self.Width = self.IHDR.IHDRWidth(self.intlist)
        self.Height = self.IHDR.IHDRHeight(self.intlist)
        self.BitDepth = self.IHDR.IHDRBitDepth(self.intlist)
        self.ColorType = self.IHDR.IHDRColorType(self.intlist)
        self.ComMethod = self.IHDR.IHDRComMethod(self.intlist)
        self.FilMethod = self.IHDR.IHDRFilMethod(self.intlist)
        self.IntMethod = self.IHDR.IHDRIntMethod(self.intlist)

        # 处理自身的rgb
        fillist = []
        decompress = list(self.decompress_idat())
        for i in range(self.Height):
            a = decompress.pop(i*self.Width*3)
            a = bytes_to_int(a)
            fillist.append(a)
        self.rlist = []
        self.glist = []
        self.blist = []
        rgblist = []
        for i in decompress:
            rgblist.append(int(i.hex(), 16))
        for i in range(len(rgblist)):
            a = rgblist[i]
            if i % 3 == 0:
                self.rlist.append(a)
            elif i % 3 == 1:
                self.glist.append(a)
            else:
                self.blist.append(a)
        self.rlist = getrgb(self, self.rlist, fillist)
        self.glist = getrgb(self, self.glist, fillist)
        self.blist = getrgb(self, self.blist, fillist)
        self.gray = False

    def decompress_idat(self):
        outlist = []
        for i in self.cklist:
            if i.Type == "IDAT":
                outlist.extend(self.byteslist[i.Dataindex:i.Dataindex+i.Length])
        outlist = struct.pack(str(len(outlist))+"c", *outlist)
        outlist = zlib.decompress(outlist)
        outlist = struct.unpack(str(len(outlist))+"c", outlist)

        return outlist

    def xy_to_rgbindex(self, x, y):
        if x == 0:
            index = y
        else:
            index = x*self.Width+y
        return index

    def modify_png(self, rlist, glist, blist):
        idat = []
        filter0 = 0
        insertindex = 0
        for i in range(len(rlist)):
            if i % self.Width == 0:
                idat.append(filter0.to_bytes(1, "big", signed=False))
            idat.append(rlist[i].to_bytes(1, "big", signed=False))
            idat.append(glist[i].to_bytes(1, "big", signed=False))
            idat.append(blist[i].to_bytes(1, "big", signed=False))
        idat = struct.pack(str(len(idat))+'c', *idat)
        idat = zlib.compress(idat)
        idat = struct.unpack(str(len(idat))+'c', idat)
        for i in range(len(self.cklist)):
            if self.cklist[i].Type == "IDAT":
                insertindex = i
                break
        for i in self.cklist:
            if i.Type == "IDAT":
                del i
        insertlist = createidat(idat)
        for i in range(len(insertlist)):
            self.cklist.insert(insertindex, insertlist[i])

    def repack(self):
        packls = []
        packls.extend(self.pnghead)
        for i in range(len(self.cklist)):
            packls.extend(self.cklist[i].bLength)
            packls.extend(self.cklist[i].bType)
            packls.extend(self.cklist[i].bData)
            packls.extend(self.cklist[i].bCRC)
        outpack = struct.pack(str(len(packls))+"c", *packls)
        return outpack

    def changegray(self):
        for i in range(len(self.rlist)):
            gray = (self.rlist[i] * 30 + self.glist[i] * 59 + self.blist[i] * 11) // 100

            self.rlist[i] = self.glist[i] = self.blist[i] = gray
        self.modify_png(self.rlist, self.glist, self.blist)
        self.gray = True

    def getchpainting(self, intervel=10):
        if not self.gray:
            self.changegray()
        outtxt = ''
        x = 1
        y = 1
        count = 0
        while x < self.Height-1:
            while y < self.Width-1:
                index = self.xy_to_rgbindex(x, y)
                if self.rlist[index] < 30:
                    outtxt += '、'
                elif self.rlist[index] < 60:
                    outtxt += '巳'
                elif self.rlist[index] < 90:
                    outtxt += '凹'
                elif self.rlist[index] < 120:
                    outtxt += '刘'
                elif self.rlist[index] < 150:
                    outtxt += '星'
                elif self.rlist[index] < 180:
                    outtxt += '倒'
                elif self.rlist[index] < 210:
                    outtxt += '隧'
                else:
                    outtxt += '齉'
                y += intervel
                count += 1
            outtxt += '\n'
            x += intervel
            y = 1
        return outtxt

    def changeedge(self):
        if not self.gray:
            self.changegray()
        graylist = []
        graylist.extend(self.rlist)
        for x in range(1, self.Height-1):
            for y in range(1, self.Width-1):
                # b c d
                # e a f
                # g h i
                index = self.xy_to_rgbindex(x, y)
                # a = graylist[self.xy_to_rgbindex(x, y)]
                b = graylist[self.xy_to_rgbindex(x-1, y-1)]
                c = graylist[self.xy_to_rgbindex(x-1, y)]
                d = graylist[self.xy_to_rgbindex(x-1, y+1)]
                e = graylist[self.xy_to_rgbindex(x, y-1)]
                f = graylist[self.xy_to_rgbindex(x, y+1)]
                g = graylist[self.xy_to_rgbindex(x+1, y-1)]
                h = graylist[self.xy_to_rgbindex(x+1, y)]
                i = graylist[self.xy_to_rgbindex(x+1, y+1)]
                fx = abs((2 * f + d + i - 2 * e - b - g)) // 4
                fy = abs((2 * h + g + i - 2 * c - b - d)) // 4
                gradient = int((fx ** 2 + fy ** 2) ** 0.5)
                if gradient > 255:
                    gradient = 255
                gradient = 255 - gradient
                self.rlist[index] = self.glist[index] = self.blist[index] = gradient

        self.modify_png(self.rlist, self.glist, self.blist)


# 重构函数
def getrgb(picture, rgblist, filtermethod):
    for i in range(picture.Height):
        if filtermethod[i] == 0:
            continue
        elif filtermethod[i] == 1:
            for j in range(picture.Width - 1):
                a = rgblist[j + i * picture.Width]
                rgblist[j + 1 + i * picture.Width] = (a + rgblist[j + 1 + i * picture.Width]) % 256
        elif filtermethod[i] == 2:
            for j in range(picture.Width):
                b = rgblist[j + (i-1) * picture.Width]
                rgblist[j + i * picture.Width] = (b + rgblist[j + i * picture.Width]) % 256
        elif filtermethod[i] == 3:
            for j in range(picture.Width):
                if j == 0:
                    b = rgblist[(i - 1) * picture.Width]
                    rgblist[i * picture.Width] = (b//2 + rgblist[i * picture.Width]) % 256
                else:
                    a = rgblist[j - 1 + i * picture.Width]
                    b = rgblist[j + (i - 1) * picture.Width]
                    rgblist[j + i * picture.Width] = ((a+b)//2 + rgblist[j + i * picture.Width]) % 256
        elif filtermethod[i] == 4:
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


# 过滤函数
def filrgb(picrgblist, filtermethod):
    pass

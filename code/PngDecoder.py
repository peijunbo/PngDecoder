import struct
import zlib
import cv2
import os


# 创建数据块类每个类变量内有该数据块的信息
class Chunk:
    def __init__(self, index, bytesls, intlist):
        self.bLength = bytesls[index:index+4]
        self.Length = intlist[index]*(16**6) + intlist[index+1]*(16**4) + intlist[index + 2]*(16**2) + intlist[index + 3]
        index += 4
        self.bType = bytesls[index:index + 4]
        self.Type = chr(intlist[index]) + chr(intlist[index+1]) + chr(intlist[index+2]) + chr(intlist[index+3])
        index += 4

        # 处理数据块
        self.Dataindex = index

        self.Data = intlist[index:index+self.Length]
        self.bData = list(bytesls[index:index+self.Length])
        index += self.Length
        # CRC
        self.bCRC = bytesls[index:index + 4]
        # self.CRC = [list[index], list[index+1], list[index+2], list[index+3]]
        self.endindex = index + 4

    def IHDRWidth(self, intlist):
        if self.Type == "IHDR":
            Width = intlist[self.Dataindex]*(16**6) + intlist[self.Dataindex+1]*(16**4) + intlist[self.Dataindex + 2]*(16**2) + intlist[self.Dataindex + 3]
            return Width

    def IHDRHeight(self, intlist):
        if self.Type == "IHDR":
            Height = intlist[self.Dataindex+4]*(16**6) + intlist[self.Dataindex+5]*(16**4) + intlist[self.Dataindex + 6]*(16**2) + intlist[self.Dataindex + 7]
            return Height

    def IHDRBitDepth(self, intlist):
        if self.Type == "IHDR":
            BitDepth = intlist[self.Dataindex + 8]
            return BitDepth

    def IHDRColorType(self, intlist):
        if self.Type == "IHDR":
            ColorType = intlist[self.Dataindex + 9]
            return ColorType

    def IHDRComMethod(self, intlist):
        if self.Type == "IHDR":
            ComMethod = intlist[self.Dataindex + 10]
            return ComMethod

    def IHDRFilMethod(self, intlist):
        if self.Type == "IHDR":
            FilMethod = intlist[self.Dataindex + 11]
            return FilMethod

    def IHDRIntMethod(self, intlist):
        if self.Type == "IHDR":
            IntMethod = intlist[self.Dataindex + 12]
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
        ck = Chunk(index, originls, intlist=ls)
        outlist.append(ck)
        index = ck.endindex
    return outlist


def createidat(idatlist):
    num = 2 ** 31 - 1
    outlist = []
    # Type
    typelist = []
    for i in [73, 68, 65, 84]:
        typelist.append(i.to_bytes(1, "big", signed=False))
    while len(idatlist) > 2**31-1:
        chunk = []
        # Length
        lengthlist = [255, 255, 255, 255]
        for i in range(len(lengthlist)):
            lengthlist[i] = lengthlist[i].to_bytes(1, "big", signed=False)
        chunk.extend(lengthlist)
        # Type
        chunk.extend(typelist)
        # Data
        chunk.extend(idatlist[:num])
        # CRC
        typelist.extend(idatlist[:num])
        crc = (zlib.crc32(struct.pack('>c', *typelist))).to_bytes(4, 'big', signed=False)
        crclist = list(struct.unpack('4c', crc))
        chunk.extend(crclist)
        intchunk = bytes_to_int(chunk)
        for i in range(len(crclist)):
            a = crclist[i]
            crclist[i] = a.to_bytes(1, "big", signed=False)
        outlist.append(Chunk(0, chunk, intchunk))
        del idatlist[:num]
    chunk = []
    # Length
    length = len(idatlist).to_bytes(4, "big", signed=False)
    length = struct.unpack("4c", length)
    chunk.extend(length)
    # Type
    chunk.extend(typelist)
    # Data
    chunk.extend(idatlist)
    # CRC
    typelist.extend(idatlist)
    crc = (zlib.crc32(struct.pack(str(len(idatlist)+4) + 'c', *typelist))).to_bytes(4, 'big', signed=False)
    crclist = list(struct.unpack('4c', crc))
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
        if self.ColorType == 0:
            self.gray = True
        else:
            self.gray = False
        if self.gray:
            pass
        else:
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

    def decompress_idat(self):
        outlist = []
        for i in self.cklist:
            if i.Type == "IDAT":
                outlist.extend(i.bData)
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

    def modify_graypng(self, graylist):
        self.graylist = graylist
        idat = []
        filter0 = 0
        insertindex = 0
        for i in range(len(graylist)):
            if i % self.Width == 0:
                idat.append(filter0.to_bytes(1, "big", signed=False))
            idat.append(graylist[i].to_bytes(1, "big", signed=False))
        idat = struct.pack(str(len(idat)) + 'c', *idat)
        idat = zlib.compress(idat)
        idat = struct.unpack(str(len(idat)) + 'c', idat)
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
        if self.gray:
            pass
        else:
            self.cklist[0].Data[9] = 0
            self.cklist[0].bData[9] = self.cklist[0].Data[9].to_bytes(1, "big", signed=False)
            self.cklist[0].bCRC = list(struct.unpack('4c',  zlib.crc32(
                struct.pack('17c', *self.cklist[0].bType, *self.cklist[0].bData)).to_bytes(4, 'big', signed=False)))
            self.gray = True
            del self.rlist
            del self.glist
            del self.blist

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
        # for i in range(len(self.rlist)):
        #     gray = (self.rlist[i] * 30 + self.glist[i] * 59 + self.blist[i] * 11) // 100
        #
        #     self.rlist[i] = self.glist[i] = self.blist[i] = gray
        # self.modify_png(self.rlist, self.glist, self.blist)
        # self.gray = True
        graylist = []
        for i in range(len(self.rlist)):
            graylist.append((self.rlist[i] * 30 + self.glist[i] * 59 + self.blist[i] * 11) // 100)
        self.modify_graypng(graylist)

    def getchpainting(self, step=10):
        if not self.gray:
            self.changegray()
        outtxt = ''
        for x in range(1, self.Height-1, step):
            for y in range(1, self.Width-1, step):
                index = self.xy_to_rgbindex(x, y)
                if self.rlist[index] < 30:
                    outtxt += '齉'
                elif self.rlist[index] < 60:
                    outtxt += '隧'
                elif self.rlist[index] < 90:
                    outtxt += '倒'
                elif self.rlist[index] < 120:
                    outtxt += '星'
                elif self.rlist[index] < 150:
                    outtxt += '刘'
                elif self.rlist[index] < 180:
                    outtxt += '凹'
                elif self.rlist[index] < 210:
                    outtxt += '巳'
                else:
                    outtxt += '、'
        return outtxt

    def changeedge(self):
        if not self.gray:
            self.changegray()
        graylist = []
        graylist.extend(self.graylist)
        for x in range(1, self.Height-1):
            for y in range(1, self.Width-1):
                # b c d
                # e a f
                # g h i
                index = self.xy_to_rgbindex(x, y)
                a = self.xy_to_rgbindex(x, y)
                # b = graylist[self.xy_to_rgbindex(x-1, y-1)]
                # c = graylist[self.xy_to_rgbindex(x-1, y)]
                # d = graylist[self.xy_to_rgbindex(x-1, y+1)]
                # e = graylist[self.xy_to_rgbindex(x, y-1)]
                # f = graylist[self.xy_to_rgbindex(x, y+1)]
                # g = graylist[self.xy_to_rgbindex(x+1, y-1)]
                # h = graylist[self.xy_to_rgbindex(x+1, y)]
                # i = graylist[self.xy_to_rgbindex(x+1, y+1)]
                b = graylist[a-self.Width-1]
                c = graylist[a-self.Width]
                d = graylist[a-self.Width+1]
                e = graylist[a-1]
                f = graylist[a+1]
                g = graylist[a+self.Width-1]
                h = graylist[a+self.Width]
                i = graylist[a+self.Width+1]
                fx = abs((2 * f + d + i - 2 * e - b - g)) // 4
                fy = abs((2 * h + g + i - 2 * c - b - d)) // 4
                gradient = int((fx ** 2 + fy ** 2) ** 0.5)
                if gradient > 255:
                    gradient = 255
                gradient = 255 - gradient
                self.graylist[index] = gradient

        self.modify_graypng(self.graylist)

    def createpng(self, pngname='test.png'):
        pngfile = open(pngname, mode='wb')
        content = self.repack()
        pngfile.write(content)
        pngfile.close()


# 处理并生成视频
def create_video(videopath, outpath, outtype=None):
    video = cv2.VideoCapture(videopath)
    fps = int(video.get(cv2.CAP_PROP_FPS))
    size = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    outvideo = cv2.VideoWriter(outpath, -1, fps, size)
    success, img = video.read()
    num = 0
    while success:
        pngname = str(num) + '.png'
        cv2.imwrite(pngname, img)
        png = PNG(pngname)
        png.changegray()
        png.createpng(pngname=pngname)
        num += 1
        success, img = video.read()
        finalpng = cv2.imread(pngname)
        outvideo.write(finalpng)
        os.remove(pngname)
    video.release()


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

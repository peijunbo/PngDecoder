import struct


#图片地址
Paddress1 = "C:\\Users\裴俊博\Desktop\实习题-实现png解码器\后端组实习题PngDecoder\\task1\\test1.png"
Paddress2 = "C:\\Users\裴俊博\Desktop\实习题-实现png解码器\后端组实习题PngDecoder\\task1\\test2.png"

#输出的文件地址
txtaddress1 = "..\\docs\\test1.txt"
txtaddress2 = "..\\docs\\test2.txt"

picture1 = open(Paddress1, mode = "rb")
picture2 = open(Paddress2, mode = "rb")

context1 = picture1.read()
context1 = struct.unpack(str(len(context1)) + "c", context1)
context2 = picture2.read()
context2 = struct.unpack(str(len(context2)) + "c", context2)
#建一个记录的列表
intlist1 = []
hexlist1 = []
intlist2 = []
hexlist2 = []
for i in context1:
    a = i.hex()
    a = int(a,16)
    intlist1.append(a)
    a = hex(int(a))
    hexlist1.append(a)

for i in context2:
    a = i.hex()
    a = int(a,16)
    intlist2.append(a)
    a = hex(int(a))
    hexlist2.append(a)

#创建数据块类每个类变量内有该数据块的信息
class chunk:
    def __init__(self, index, list):
        self.Length = list[index]*(16**6) + list[index+1]*(16**4) + list[index + 2]*(16**2) + list[index + 3]
        index += 4
        self.Type = chr(list[index]) + chr(list[index+1]) + chr(list[index+2]) + chr(list[index+3])
        index += 4

        #目前还不处理数据因此跳过数据块数据

        index += self.Length
        #CRC
        self.CRC = [list[index], list[index+1], list[index+2], list[index+3]]
        self.endindex = index + 4
#将所有数据块读取存入列表中
initindex = 8

def setchunk(index, list):
    outlist = []
    while index < len(list):
        ck = chunk(index, list)
        outlist.append(ck)
        index = ck.endindex
    return outlist
#打印数据块
chunklist1 = setchunk(initindex, intlist1)
chunklist2 = setchunk(initindex, intlist2)


#将结果写入文件中
shuchu1 = open(txtaddress1,"w")
shuchu1.write("Length")
shuchu1.write("\t")
shuchu1.write("Type")
shuchu1.write("\t")
shuchu1.write("CRC")
shuchu1.write("\n")

for i in chunklist1:
    shuchu1.write(str(i.Length))
    shuchu1.write("\t")
    shuchu1.write(str(i.Type))
    shuchu1.write("\t")
    shuchu1.write(str(i.CRC))
    shuchu1.write("\n")

shuchu2 = open(txtaddress2, "w")
shuchu2.write("Length")
shuchu2.write("\t")
shuchu2.write("Type")
shuchu2.write("\t")
shuchu2.write("CRC")
shuchu2.write("\n")

for i in chunklist2:
    shuchu2.write(str(i.Length))
    shuchu2.write("\t")
    shuchu2.write(str(i.Type))
    shuchu2.write("\t")
    shuchu2.write(str(i.CRC))
    shuchu2.write("\n")


picture1.close()
picture2.close()
shuchu1.close()
shuchu2.close()
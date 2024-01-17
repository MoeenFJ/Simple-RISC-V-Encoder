#!/usr/bin/env python3

from bitstring import Bits
import sys


def ParseRegister(a):
    a = a.lower()
    try:
        if a[0] != 'x':
            print(f"Invalid register name : {a}")
            quit()

        r = a[1:]
        r = int(r)

        if r >= 32 or r < 0:
            print(f"Invalid register name : {a}")
            quit()

        return r
    except:
        print(f"Invalid register name : {a}")
        quit()


def ParseImm(a):

    try:
        b = int(a)
        return b
    except:
        print(f"Invalid Immidiate : {a}")
        quit()


def ParseAddress(a):
    try:
        t = a.split('(', 1)
        Imm = ParseImm(t[0])
        t = t[1].split(')', 1)[0]
        Reg = ParseRegister(t)

        return (Reg, Imm)
    except:
        print(f"Invalid Address : {a}")
        quit()


def OpDetect(op):
    found = None
    for inner_array in opcodes:
        if inner_array[0] == op:
            found = inner_array
            break

    return found


opcodes = [
    # AsmOP,Opcode, func3, func7 , type
    ["add", 0x33, 0x0, 0x00, 'R'],
    ["sub", 0x33, 0x0, 0x20, 'R'],
    ["addi", 0x13, 0x0, 0x00, 'I-V'],
    ["slt", 0x33, 0x2, 0x00, 'R'],
    ["sltu", 0x33, 0x3, 0x00, 'R'],
    ["slti", 0x13, 0x2, 0x00, 'I-V'],
    ["sltiu", 0x13, 0x3, 0x00, 'I-V'],

    ["mul", 0x33, 0x0, 0x01, 'R'],
    ["mulh", 0x33, 0x1, 0x01, 'R'],
    ["mulhu", 0x33, 0x2, 0x01, 'R'],
    ["mulhsu", 0x33, 0x3, 0x01, 'R'],
    ["div", 0x33, 0x4, 0x01, 'R'],
    ["divu", 0x33, 0x5, 0x01, 'R'],
    ["rem", 0x33, 0x6, 0x01, 'R'],
    ["remu", 0x33, 0x7, 0x01, 'R'],

    ["lw", 0x03, 0x2, 0x00, 'I-A'],
    ["sw", 0x23, 0x2, 0x00, 'S'],
    ["lh", 0x03, 0x1, 0x00, 'I-A'],
    ["lhu", 0x03, 0x1, 0x00, 'I-A'],
    ["sh", 0x23, 0x1, 0x00, 'S'],
    ["lb", 0x03, 0x0, 0x00, 'I-A'],
    ["lbu", 0x03, 0x0, 0x00, 'I-A'],
    ["sb", 0x23, 0x0, 0x00, 'S'],

    ["and", 0x33, 0x7, 0x00, 'R'],
    ["or", 0x33, 0x6, 0x00, 'R'],
    ["xor", 0x33, 0x4, 0x00, 'R'],
    ["andi", 0x13, 0x7, 0x00, 'I-V'],
    ["ori", 0x13, 0x6, 0x00, 'I-V'],
    ["xori", 0x13, 0x4, 0x00, 'I-V'],

    ["sll", 0x33, 0x1, 0x00, 'R'],
    ["srl", 0x33, 0x5, 0x00, 'R'],
    ["sra", 0x33, 0x5, 0x20, 'R'],
    ["slli", 0x13, 0x1, 0x00, 'I-V'],
    ["srli", 0x13, 0x5, 0x00, 'I-V'],
    ["srai", 0x13, 0x5, 0x20, 'I-V'],

    ["beq", 0x63, 0x0, 0x00, 'B'],
    ["bne", 0x63, 0x1, 0x00, 'B'],
    ["blt", 0x63, 0x4, 0x00, 'B'],
    ["bge", 0x63, 0x5, 0x00, 'B'],
    ["bltu", 0x63, 0x6, 0x00, 'B'],
    ["bgeu", 0x63, 0x7, 0x00, 'B'],

    ["jal", 0x6F, 0x0, 0x00, 'J'],
    ["jalr", 0x67, 0x0, 0x00, 'I-A'],

    ["lui", 0x37, 0x0, 0x00, 'U']
]


def Generate(asmPath, savePath="program.o", saveType=2):
    asmPath = 'program.asm'

    asmFile = open(asmPath, 'r')

    binaryStrings = []

    lineCounter = 1
    for line in asmFile:
        instText = line.split(';')[0].strip().lower()

        if instText == "":
            continue

        print(instText)

        splitted = instText.split(' ', 1)

        instOp = splitted[0]

        args = splitted[1].split(',')

        Op = OpDetect(instOp)

        if Op == None:
            print(f"Invalid instruction on line {lineCounter} : {instOp}")
            quit()

        if Op[4] == "R":
            rd = ParseRegister(args[0].strip())
            rs1 = ParseRegister(args[1].strip())
            rs2 = ParseRegister(args[2].strip())

            binaryStrings.append('{0:07b}'.format(Op[3]) + '{0:05b}'.format(rs2) + '{0:05b}'.format(
                rs1) + '{0:03b}'.format(Op[2]) + '{0:05b}'.format(rd) + '{0:07b}'.format(Op[1]))
        elif Op[4] == "I-A":
            rd = ParseRegister(args[0].strip())
            rs1, imm = ParseAddress(args[1].strip())

            imm = Bits(int=imm, length=32).bin[::-1]

            binaryStrings.append(imm[0:12][::-1] + '{0:05b}'.format(rs1) + '{0:03b}'.format(
                Op[2]) + '{0:05b}'.format(rd) + '{0:07b}'.format(Op[1]))
        elif Op[4] == "I-V":
            rd = ParseRegister(args[0].strip())
            rs1 = ParseRegister(args[1].strip())
            imm = ParseImm(args[2].strip())

            imm = Bits(int=imm, length=32).bin[::-1]

            binaryStrings.append(imm[0:12][::-1] + '{0:05b}'.format(rs1) + '{0:03b}'.format(
                Op[2]) + '{0:05b}'.format(rd) + '{0:07b}'.format(Op[1]))
        elif Op[4] == "J":
            rd = ParseRegister(args[0].strip())
            imm = ParseImm(args[1].strip())

            imm = Bits(int=imm, length=32).bin[::-1]

            binaryStrings.append(imm[20][::-1] + imm[1:11][::-1] + imm[10][::-1] +
                                 imm[12:20][::-1] + '{0:05b}'.format(rd) + '{0:07b}'.format(Op[1]))  # Check
        elif Op[4] == "S":
            rd = ParseRegister(args[0].strip())
            rs1, imm = ParseAddress(args[1].strip())

            imm = Bits(int=imm, length=32).bin[::-1]

            binaryStrings.append(imm[5:12][::-1] + '{0:05b}'.format(rd) + '{0:03b}'.format(
                rs1) + '{0:05b}'.format(Op[2]) + imm[0:5][::-1] + '{0:07b}'.format(Op[1]))
        elif Op[4] == "U":
            rd = ParseRegister(args[0].strip())
            imm = ParseImm(args[1].strip())

            imm = Bits(int=imm, length=32).bin[::-1]

            binaryStrings.append(
                imm[0:20][::-1] + '{0:05b}'.format(rd) + '{0:07b}'.format(Op[1]))  # Check
        elif Op[4] == "B":
            rd = ParseRegister(args[0].strip())
            rs1 = ParseRegister(args[1].strip())
            imm = ParseImm(args[2].strip())

            imm = Bits(int=imm, length=32).bin[::-1]

            binaryStrings.append(imm[12][::-1] + imm[5:11][::-1] + '{0:05b}'.format(rs1) + '{0:05b}'.format(
                rd) + '{0:03b}'.format(Op[2]) + imm[1:5][::-1] + imm[11][::-1] + '{0:07b}'.format(Op[1]))

        lineCounter += 1

    print(binaryStrings)
    
    # saveType 0=8Bit Per Line, 1=32Bit Per Line, 2=RawBin

    if saveType == 0:
        f = open(savePath, "w")
        for line in binaryStrings:
             f.write(line[24:32]+"\n"+line[16:24]+"\n" +
                    line[8:16]+"\n"+line[0:8]+"\n")
        f.close()
    elif saveType == 1:
        f = open(savePath, "w")
        for line in binaryStrings:
            f.write(line[0:8]+"\n"+line[8:16]+"\n" +
                    line[16:24]+"\n"+line[24:32]+"\n")
        f.close()
    elif saveType == 2:
        f = open(savePath, "w")
        for line in binaryStrings:
            f.write(line+"\n")
        f.close()
    elif saveType == 3:
        f = open(savePath, "wb")
        for line in binaryStrings:
            f.write(bytes(bytearray([int(line[24:32],2),int(line[16:24],2),int(line[8:16],2),int(line[0:8],2)])))    
        f.close()
    elif saveType == 4:
        f = open(savePath, "wb")
        for line in binaryStrings:
            f.write(bytes(bytearray([int(line[0:8],2),int(line[8:16],2),int(line[16:24],2),int(line[24:32],2)])))    
        f.close()


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(
            "Usage : ./RVE.py <input asm file name> [output filename] [save type=1] \navailable save types : \n 0 : Divide each instaction to 4 lines (4*8 Little endian) \n 1 : Divide each instaction to 4 lines (4*8 Big endian) \n 2 : Write each instruction in one line (1*32) \n 3 : Raw binary (Little endian)  \n 4 : Raw binary (Big endian)")
        quit()
    asmPath = sys.argv[1]

    if len(sys.argv) == 2:
        Generate(asmPath=asmPath)
    elif len(sys.argv) == 3:
        Generate(asmPath=asmPath, savePath=sys.argv[2])
    elif len(sys.argv) == 4:
        saveType = int(sys.argv[3])
        if (saveType not in [0,1,2,3,4]):
            print(f"Invalid save type : {saveType}, available save types : \n 0 : Divide each instaction to 4 lines (4*8 Little endian) \n 1 : Divide each instaction to 4 lines (4*8 Big endian) \n 2 : Write each instruction in one line (1*32) \n 3 : Raw binary (Little endian) \n 4 : Raw binary (Big endian)")
            quit()
        Generate(asmPath=asmPath, savePath=sys.argv[2], saveType=saveType)

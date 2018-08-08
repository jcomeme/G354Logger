import sys
import serial


class GController:
    def __init__(self, tty, baud = 460800):
        self.ser = serial.Serial(tty, baud, timeout=0.1)
        #print(self.ser.timeout)




    def readRegister(self, registerAddress, windowID):
        #windowIDとレジスタアドレスのbytesからbytes型のリストを返す
        self.ser.write(b'\xfe')
        self.ser.write(windowID)
        self.ser.write(b'\x0d')

        self.ser.write(registerAddress)
        self.ser.write(b'\x00')
        self.ser.write(b'\x0d')
        
        response = []
        while 1:
            c = self.ser.read()
            if c is None:
                break
            response.append(c)
            #if c == bytes.fromhex("0d"):
            if c == b'\x0d':
                break

        return response



    def writeRegister(self, registerAddress, value, windowID):

        self.ser.write(b'\xfe')
        self.ser.write(windowID)
        self.ser.write(b'\x0d')
        
        self.ser.write((int.from_bytes(registerAddress, 'big') + int.from_bytes(b'\x80', 'big')).to_bytes(1, 'big'))
        self.ser.write(value)
        self.ser.write(b'\x0d')
        




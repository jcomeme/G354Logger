import sys
import os
import serial
import G354Controller
from time import sleep



def s16(value):
    return -(value & 0b1000000000000000) | (value & 0b0111111111111111)


tty = ''
baud = 460800


ls = os.listdir('/dev')

lsarr = []
inputmessage = 'どのデバイスを使いますか？\n'

ctr = 1
for item in ls:
    if item.find('tty.usbserial') > -1:
        lsarr.append(item)
        inputmessage += str(ctr) + '  ' + item + '\n'
        ctr += 1
if len(lsarr) == 0:
    lsarr = os.listdir('/dev')
    ctr = 1
    for dev in lsarr:
        inputmessage += str(ctr) + '  ' + dev + '\n'
        ctr += 1
    inputmessage += 'それらしいデバイスがないのでUSBがつながってないのかも';

while True:
        answer = input(inputmessage)
        if answer == "":
            print('')
        elif answer.isdecimal():
            num = int(answer) - 1
            tty = '/dev/' + lsarr[num]
            break
        else:
            print('数字で入力してください')

controller = G354Controller.GController(tty, baud)


args = sys.argv
path = ''
if len(args) > 1:
    path = args[1]


controller.writeRegister(b'\x0a', b'\x80', b'\x01')#ソフトリセット
sleep(0.8)#800ms待つ

controller.writeRegister(b'\x03', b'\x01', b'\x00')#サンプリングモードに移行
#UART受信バッファをクリアしてるつもり
controller.ser.write(b'\x02')
controller.ser.write(b'\x00')
controller.ser.write(b'\x0d')
while controller.ser.read():
    sleep(0)


controller.writeRegister(b'\x03', b'\x02', b'\x00')#コンフィグモードへ移行

controller.writeRegister(b'\x05', b'\x00', b'\x01')#dout rate 設定。00で2000SPS, 値が1増えるごとに1/2になる
controller.writeRegister(b'\x08', b'\x01', b'\x01')#UART設定。末尾ビット0で手動、1で自動
controller.writeRegister(b'\x0c', b'\x02', b'\x01')#バースト制御。- - - - - GPIO_OUT COUNT_OUT CHKSM_OUT
controller.writeRegister(b'\x0d', b'\x70', b'\x01')#バースト制御。FLAG_OUT TEMP_OUT GYRO_OUT ACCL_OUT - - - -
controller.writeRegister(b'\x0f', b'\x00', b'\x01')#バースト制御。- TEMP_BIT GYRO_BIT ACCL_BIT - - - -#0で16bit, 1で32bit


controller.writeRegister(b'\x03', b'\x01', b'\x00')#サンプリングモードに移行


#サンプリング開始
controller.ser.write(b'\x80')
controller.ser.write(b'\x00')
controller.ser.write(b'\x0d')

linebuffer = '';
highflag = False
highbuffer = 0

counter = 0

if path != '':
    with open(path, mode='w') as f:
        f.write('address, temp, gyro_x, gyro_y, gyro_z, accl_x, accl_x, accl_x, count, delimiter\n')


while 1:
    for item in range(0, 18):
        c = controller.ser.read()

        if c == None:
            break
        if item == 17:
            linebuffer += str(int.from_bytes(c, 'big'))
            #if counter == 10:
            if True:
                print(linebuffer)
                if path != '':
                    with open(path, mode='a') as f:
                        f.write(linebuffer + '\n')
                counter = 0
            highbuffer = 0
            linebuffer = ''
        else:
            if highflag:
                highbuffer = int.from_bytes(c, 'big')<<8
            else:
                if item == 0:
                    linebuffer += str(int.from_bytes(c, 'big') + highbuffer)
                elif item < 3:#TEMP
                    linebuffer += str(round(s16((int.from_bytes(c, 'big') + highbuffer) -2634) * (-0.0037918) + 25, 2))
                elif item < 9:#gyro
                    linebuffer += str(round(s16(int.from_bytes(c, 'big') + highbuffer) * 0.016, 2))
                elif item < 15:#accl
                    linebuffer += str(round(s16(int.from_bytes(c, 'big') + highbuffer) * 0.2, 2))
                else:#accl
                    linebuffer += str((int.from_bytes(c, 'big') + highbuffer))
                linebuffer += ','
        highflag = not highflag




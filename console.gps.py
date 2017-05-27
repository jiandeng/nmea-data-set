import serial.tools.list_ports as listports
import serial
import signal
import time
import sys
import shutil

# Ctrl^C
def quit(signum, frame):
    shutil.copy('gps.txt', time.strftime('GPS-%Y%m%dT%H%M%S.txt'))
    sys.exit()

def main_func():
    global ser
    # choose serial port
    port = None
    ports = map(lambda x: x[0], listports.comports())
    if len(ports) == 0:
        print 'No comport to use!'
    else:
        print '\nSelect a comport to continue:'
        for i in range(len(ports)):
            print '  ({}) - {}'.format(i, ports[i])
        try:
            c = int(raw_input())
        except:
            print 'Invalid choice!'
        if c >= 0 and c < len(ports):
            port = ports[c]
        else:
            print 'Invalid choice'

    out = open('gps.txt', 'w')
    out.write(time.strftime('%Y-%m-%dT%H:%M:%S\r\n'))
    out.close()

    # open serial port
    if port != None:
        print '\nOpening {}'.format(port)
        ser = serial.Serial(port, 115200)
        # connect request
        print 'Waiting...'
        ser.timeout = 3
        while True:
            req = ser.readline()
            if req is not None and req != '':
                s = time.strftime('%Y-%m-%dT%H:%M:%S -->> ', time.localtime()) + req
                print s
                out = open('gps.txt', 'a')
                out.write(s)
                out.close()


if __name__ == '__main__':
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)
    main_func()

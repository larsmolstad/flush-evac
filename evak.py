# from ctypes import windll
# import winioport as w

import time 
import RPi.GPIO as gpio
import warnings
VAK_PIN = 18
HE_PIN = 16
logfile = "/home/pi/evaklog.txt"

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    gpio.setmode(gpio.BOARD)    
    gpio.setup(VAK_PIN, gpio.OUT)
    gpio.setup(HE_PIN, gpio.OUT)

def set_he_valve(state):
    gpio.output(HE_PIN, {'open':True, 'closed': False}[state])

def set_vak_valve(state):
    gpio.output(VAK_PIN, {'open':True, 'closed': False}[state])
        
log_users = True

docstr = """
          Usage: Write command and press return.
          
           Turn vacuum on:
           
          >>> vac()
          
           Turn Helium on:
           
          >>> he()
          
           Close both valves:
           
          >>> close()
          
           Rinse and fill with He: fill(cycles , vactime, hetime, endtime)
           
          >>> fill(3, 30, 40, 30)
          
           Rinse and evacuate:  rinse(cycles , vactime, hetime, endtime)
           
          >>> rinse(3, 30, 40, 30)

           Log out:
           
          >>> logout()

          Let the pump run for at least 30 minutes before starting, and
          60 minutes after finishing handling liquid bottles.
"""
last_login_time = [0]
logined_user = ['']
def login():
    if (not logined_user[0]) or time.time() - last_login_time[0]>3600:
        logined_user[0] = raw_input('Logged out. Please enter your name:\n')
        f = open(logfile,'a')
        f.write(time.ctime() + '  ' + logined_user[0]+'\n')
        f.close()
        last_login_time[0] = time.time()

class Logout(object):
        def __call__(self):
                logined_user[0] = ''
                login()
        def __repr__(self):
                self.__call__()
                return ''

logout = Logout()

def doc():
    print(docstr)

def vac():
    """ closes the Helium valve and opens the vacuum valve"""
    set_he_valve('closed')
    time.sleep(0.1)
    set_vak_valve('open')

def he():
    """ closes the vacuum valve and opens the Helium valve"""
    set_vak_valve('closed')
    time.sleep(0.1)
    set_he_valve('open')

def close():
    set_he_valve('closed')
    set_vak_valve('closed')

vak=vac
He = he
lukk = close

def wait(t,mark=False):
    t0 = time.time()
    t1=t0
    tmark = t0 
    while t1-t0<t:
        time.sleep(.1)
        t1 = time.time()
        if mark and t1-tmark>mark:
            print ".",
            tmark = t1
    if mark:
        print('')
        
def remember():
        then = time.ctime(time.time()+3600)[11:16]
        print '\nLet the pump run for at least 60 minutes (until %s)'%then
        print 'Remember to close the Helium valve'

def fill(cycles=3,vactime=30,hetime=40,endtime=30):
    login()
    print repr(cycles)+' cycles, vactime='+repr(vactime)+' hetime='+repr(hetime),' endtime='+repr(endtime)
    for i in range(cycles):
        print
        print 'vak ',
        lukk();vac();wait(vactime,10)
        print ' he ',
        lukk();he();wait(hetime,10)
    wait(endtime,10)
    lukk()
    print 'closed'
    #winsound.Beep(1000,100)
    remember()
        
def rinse(cycles=3, vactime=90, hetime=30, endtime=30):
    login()
    print repr(cycles)+' cycles, vactime='+repr(vactime)+' hetime='+repr(hetime),' endtime='+repr(endtime)
    for i in range(cycles):
        print 'vak,',  
        lukk();vac();wait(vactime,10)
        print ' he, ',
        lukk();he();wait(hetime,10)
    print 'vak,',  
    lukk();vac();wait(vactime,10)
    wait(endtime,10)
    #winsound.Beep(1000,100)
    remember()

login()

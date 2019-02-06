
#
# This code requires python3!
# Todo : detect and bom-out if using python2 
#

import termios, os, time, sys
PRE            = 0xA0
POST           = 0x50

CMD_OPMODE     = 0x01 # <ID> <mode>
CMD_STOPSHORT  = 0x02 # <ID> <stopmask> 
CMD_BRD_STATUS = 0x03 # <ID> 
CMD_LINFREQ    = 0x04 # <ID> <MS><LS> 
CMD_LINDC      = 0x05 # <ID> <MS><LS>
CMD_LINON      = 0x06 # <ID> <dir>
CMD_GET_ERROR  = 0x07 # <ID> 
CMD_STEP       = 0x08 # <ID> <MS><MM><LS>
CMD_STEPFREQ   = 0x09 # <ID> <MS><MM><LS>
CMD_STOPALL    = 0x0A # 0x81
CMD_STOP2ND    = 0x81 #
CMD_OD         = 0x0B # <ID> <on/off>
CMD_DAC        = 0x0C # <ID> <MS><LS>
CMD_GET_ADC    = 0x0D # <ID> <MS><LS>
CMD_READIO     = 0x0E # <ID> <MS><MM><LS>
CMD_WRITEIO    = 0x0F # <ID> <MS><MM><LS>
CMD_SETIO      = 0x10 # <ID> <MS><MM><LS>
CMD_SETADCDAC  = 0x11 # <ID> <ADC><DAC>
CMD_CONFIGURE  = 0x12 # <ID> <MS><LS>
CMD_VERSION    = 0x13 # <ID>
CMD_MOT_STATUS = 0x14 # <ID>
CMD_SYNC       = 0x15 # 0x18
CMD_POLL       = 0x16 # <ID>
CMD_PWR_OFF    = 0x17 # 0x81
CMD_IO_STATUS  = 0x18 # <ID>
CMD_DCC_MESS   = 0x19 # <ID> <format> <d0> <d1> <d2> <d3> <d4>
CMD_DCC_CONFIG = 0x1A # <ID> <repeat> <preamble> <dc_ms> <dc_ls>
CMD_MOT_CONFIG = 0x1B # <ID> 
CMD_MOT_MISSED = 0x1C # <ID>
CMD_SET_RAMP   = 0x1D # <ID> <up|down> <hlt>
CMD_ENDSTOP    = 0x1F # <ID> <type> <timeA> <timeB>
CMD_SHORTHOT   = 0x21 # <ID> <short> 
CMD_SETBAUD    = 0x22 # 18 81 <baud>
CMD_QUAD       = 0x23 # Quadrature encoder on 
CMD_QUAD_READ  = 0x24 # Get value
CMD_QUAD_GOTO  = 0x25 # Goto position
CMD_QUAD_LIMIT = 0x26 # Set limits 
CMD_STEPRAMP   = 0x29 #

###################

MODE_OFF        = 0x00
MODE_BRUSH      = 0x01
MODE_DCC        = 0x02
MODE_STEPG_OFF  = 0x08
MODE_STEPP_OFF  = 0x09
MODE_STEPG_PWR  = 0x18
MODE_STEPP_PWR  = 0x19
MODE_STEP_MASK  = 0x0C

ENDSTOP_OFF  =  0
ENDSTOP_LOW  =  1
ENDSTOP_HIGH =  2

MOVE_STOP = 0   
MOVE_A    = 1
MOVE_B    = 2

RAMP_OFF=  0 # -
RAMP_010=  1 # 0.10 sec. 
RAMP_025=  2 # 0.25 sec.
RAMP_050=  3 # 0.50 sec.
RAMP_075=  4 # 0.75 sec.
RAMP_100=  5 # 1.00 sec.
RAMP_125=  6 # 1.25 sec.
RAMP_150=  7 # 1.50 sec.
RAMP_175=  8 # 1.75 sec.
RAMP_200=  9 # 2.00 sec.
RAMP_225= 10 # 2.25 sec.
RAMP_250= 11 # 2.50 sec.
RAMP_300= 12 # 3.00 sec.
RAMP_400= 13 # 4.00 sec.
RAMP_500= 14 # 5.00 sec.
RAMP_700= 15 # 7.00 sec.

SHORT_NONE  = 0 # Stop nothing but reduce current
SHORT_CHAN  = 1 # Stop channel
SHORT_DUAL  = 2 # Stop channel pair
SHORT_BOARD = 3 # Stop board
SHORT_SYST  = 4 # Stop system

QUAD_EMPTY   = 0x00 # No flags
QUAD_REVERSE = 0x01 # Reverse counting
QUAD_GOSLOW  = 0x02 # GOTO & limits have slow
QUAD_TOP     = 0x04 # Have top limit
QUAD_BOT     = 0x08 # Have bottom limit
QUAD_ON      = 0x10 # ON/OFF only used in command



STOP_OFF  =  0
STOP_ON   =  1

PIN_SAME    = 0
PIN_INPUT   = 1
PIN_OUTPUT  = 2
PIN_ENDSTOP = 3
PIN_ADC     = 4
PIN_DAC     = 5
PIN_I2C     = 6

DAC_MIN = 0.7
DAC_MAX = 2.7 

filehandle = -1

# operating mode of each pin 
pin_mode = [ \
 [ 1,1,1,1,1,1,1,1, 1,1, 0,0, PIN_ADC,PIN_ADC,PIN_ADC,PIN_ADC, 0, 1, 0, 1], \
 [ 1,1,1,1,1,1,1,1, 1,1, 0,0, PIN_ADC,PIN_ADC,PIN_ADC,PIN_ADC, 0, 1, 0, 1], \
 [ 1,1,1,1,1,1,1,1, 1,1, 0,0, PIN_ADC,PIN_ADC,PIN_ADC,PIN_ADC, 0, 1, 0, 1], \
 [ 1,1,1,1,1,1,1,1, 1,1, 0,0, PIN_ADC,PIN_ADC,PIN_ADC,PIN_ADC, 0, 1, 0, 1]  \
 ]

# Which end stop is high [board][channel*2+(B?1:0)]
end_stop_high = [ 
 [ 0,0,0,0,0,0,0,0 ],
 [ 0,0,0,0,0,0,0,0 ],
 [ 0,0,0,0,0,0,0,0 ],
 [ 0,0,0,0,0,0,0,0 ]
 ]
 
# Short mode
# required to combine with endstop command 
short_mode = [ \
[ SHORT_CHAN, SHORT_CHAN, SHORT_CHAN, SHORT_CHAN ],
[ SHORT_CHAN, SHORT_CHAN, SHORT_CHAN, SHORT_CHAN ],
[ SHORT_CHAN, SHORT_CHAN, SHORT_CHAN, SHORT_CHAN ],
[ SHORT_CHAN, SHORT_CHAN, SHORT_CHAN, SHORT_CHAN ] 
]

# step freq set per board and per channel
# Half of these are unused
set_step_freq = [ 
 [0,0,0,0 ],
 [0,0,0,0 ],
 [0,0,0,0 ],
 [0,0,0,0 ]
 ]
 
 
# debug
def show_buf(str, b) :
  sys.stdout.write("%s" % str)
  for i in range(0,len(b)) :
    sys.stdout.write("%02X " % b[i])
  sys.stdout.write("\n")

# open PI uart
# 'port' argument is for future use
# First limited edition: Can use for write only
# todo : return error if open failed....
def open_uart(port):
   global filehandle
   filehandle=os.open("/dev/ttyAMA0",os.O_RDWR|os.O_NOCTTY|os.O_NDELAY|os.O_NONBLOCK)
   port_attr = termios.tcgetattr(filehandle)
   # [ iflag, oflag, cflag, lflag, ispeed, ospeed]
   #   [0]    [1]     [2]    [3]     [4]     [5]
   port_attr[0] = termios.IGNBRK
   # port_attr.c_iflag &= ~(termios.IXON|termios.IXOFF|termios.IXANY)
   port_attr[1] = 0
   port_attr[2] = port_attr[2] | termios.CLOCAL | \
                  termios.CREAD # ignore mode status, enable rec.
   port_attr[2] = port_attr[2] & ~(termios.PARENB |
                  termios.PARODD | termios.CSTOPB) # No parity, 1 stop bit
   port_attr[3] = 0
   port_attr[4] = termios.B57600
   port_attr[5] = termios.B57600
   termios.tcsetattr(filehandle,termios.TCSANOW,port_attr)


def read_uart(num_bytes) :
  if num_bytes>16 : raise Exception
  retry = 4
  buffer = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0 ]
  while (retry) :
    read_fail = 0
    try:
        buffer = os.read(filehandle, num_bytes)
    except OSError as err:
        if err.errno == os.errno.EAGAIN or err.errno == os.errno.EWOULDBLOCK:
            read_fail = 1
            pass
        else:
            raise  # something else has happened -- better reraise
    
    if read_fail==1: 
        # try again 
        retry = retry - 1
    else:
        # buffer contains some received data 
        if len(buffer)==num_bytes :
          return True, buffer
  return False, buffer


# Stop all motors 
def stop_all() :
  wrtbuf = [0xA0, CMD_STOPALL, CMD_STOP2ND, POST]
  os.write(filehandle,bytes(wrtbuf))

# Power down all motors
def emergency_stop() :
  wrtbuf = [0xA0, CMD_PWR_OFF, CMD_STOP2ND, POST]
  os.write(filehandle,bytes(wrtbuf))

# get version
# Board version MAJOR.MINOR is returned
# as MAJOR*100+MINOR
# return 0 on fail
# 
def get_version(board) :
   dest = (board<<2)
   wrtbuf = [0xA0, CMD_VERSION, dest, POST, POST, POST, POST]
   os.write(filehandle,bytes(wrtbuf))
   termios.tcdrain(filehandle)
   ok , data = read_uart(4)
   if (not ok) : # or wrtbuf[0]!=CMD_GET_ERROR or wrtbuf[1]!=dest) :
     return 0
   # convert xx.yy into xx*100+yy 
   # thus version 2.5 comes out as 205
   val = data[2]*100 + data[3]
   return val
  
# Set channel operating mode 
# board   0..3
# channel 0..3
# mode    0=odd
#         1=brushed
#         2=DCC
#         8=step gray off
#         9=step pulse off 
#        24=step gray powered
#        25=step pulse powered
#
# As extra this routine check the file handle
# as it is the most likely to be called frist (and not often)
def set_mode(board,channel,mode) :
  # To do : check the arguments
  global filehandle
  if (filehandle== -1) :
    print("Uninitialised filehandle.\nDid you forget to use 'open_uart(0)'?\n")
  dest = (board<<2) | channel
  wrtbuf = [PRE, CMD_OPMODE, dest, mode, POST]
  os.write(filehandle,bytes(wrtbuf))
  # to make life easier set default frequency 
  # for brushed or stepper mode 
  if mode==MODE_BRUSH :
    # set lin. freq 5KHz 
    wrtbuf = [PRE, CMD_LINFREQ, dest, 0x13, 0x88, POST]
    os.write(filehandle,bytes(wrtbuf))
  if mode & MODE_STEP_MASK :
    # set step freq 100 Hz (*256)
    wrtbuf = [PRE, CMD_STEPFREQ, dest, 0x00, 0x64, 0x00, POST]
    os.write(filehandle,bytes(wrtbuf))


#
# Set J3 pins as endstop
#
# stop_A, stop_B is on off:
# ENDSTOP_OFF    0
# ENDSTOP_LOW    1  Stop if pin low
# ENDSTOP_HIGH   2  Stop if pin high 
#
# return 1 on success
# return 0 on error 
def set_endstop (board,channel,stop_A,stop_B) :
   global pin_mode, end_stop_high
   # To do : check the arguments
   dest = (board<<2) | channel
   stop_mode = 0
   if (stop_A!=ENDSTOP_OFF) : stop_mode = stop_mode | 0x01
   if (stop_B!=ENDSTOP_OFF) : stop_mode = stop_mode | 0x02
   if (stop_A==ENDSTOP_HIGH): stop_mode = stop_mode | 0x04
   if (stop_B==ENDSTOP_HIGH): stop_mode = stop_mode | 0x08
   stop_mode= stop_mode | short_mode[board][channel]
   wrtbuf = [PRE, CMD_STOPSHORT, dest, stop_mode, POST]
   os.write(filehandle,bytes(wrtbuf))
   # Update the I/O status table
   pin = channel*2
   if (stop_A) :
      pin_mode[board][pin] = PIN_ENDSTOP
   else :
      pin_mode[board][pin] = PIN_INPUT
   if (stop_B) :
      pin_mode[board][pin+1] = PIN_ENDSTOP
   else :
      pin_mode[board][pin+1] = PIN_INPUT
   # Update the endstop table
   if stop_A==ENDSTOP_HIGH :
      end_stop_high[board][pin] = 1
   else :
      end_stop_high[board][pin] = 0
   if stop_B==ENDSTOP_HIGH :
      end_stop_high[board][pin+1] = 1
   else :
      end_stop_high[board][pin+1] = 0


#
# Set J3 pins as endstop
# Also sets glitch filter 
#
# stop_A, stop_B is on off:
# ENDSTOP_OFF    0
# ENDSTOP_LOW    1  Stop if pin low
# ENDSTOP_HIGH   2  Stop if pin high 
#
# return 1 on success
# return 0 on error 
def set_endstop2 (board,channel,stop_A,stop_B,filt_A,filt_B) :
   global pin_mode, end_stop_high
   # To do : check the arguments
   dest = (board<<2) | channel
   stop_mode = 0
   if (stop_A!=ENDSTOP_OFF) : stop_mode = stop_mode | 0x01
   if (stop_B!=ENDSTOP_OFF) : stop_mode = stop_mode | 0x02
   if (stop_A==ENDSTOP_HIGH): stop_mode = stop_mode | 0x04
   if (stop_B==ENDSTOP_HIGH): stop_mode = stop_mode | 0x08
   wrtbuf = [PRE, CMD_ENDSTOP, dest, stop_mode,filt_A,filt_B, POST]
   os.write(filehandle,bytes(wrtbuf))
   # Update the I/O status table
   pin = channel*2
   if (stop_A) :
      pin_mode[board][pin] = PIN_ENDSTOP
   else :
      pin_mode[board][pin] = PIN_INPUT
   if (stop_B) :
      pin_mode[board][pin+1] = PIN_ENDSTOP
   else :
      pin_mode[board][pin+1] = PIN_INPUT
   # Update the endstop table
   if stop_A==ENDSTOP_HIGH :
      end_stop_high[board][pin] = 1
   else :
      end_stop_high[board][pin] = 0
   if stop_B==ENDSTOP_HIGH :
      end_stop_high[board][pin+1] = 1
   else :
      end_stop_high[board][pin+1] = 0

#
# Set short/hot mode
# For board SW revision 2.4 and higher replaced
# with set_shorthot routine
#
def set_short(board,channel,short) :
   # if short<SHORT_NONE || short>SHORT_SYST : 
   short_mode[board][channel] = short
   short = short << 4 
   # Get the endstop data to add
   pin = channel*2
   if pin_mode[board][pin]   == PIN_ENDSTOP : short=short|0x01
   if pin_mode[board][pin+1] == PIN_ENDSTOP : short=short|0x02
   if end_stop_high[board][pin] == 1 : short=short|0x04
   if end_stop_high[board][pin+1] == 1 : short=short|0x08
   dest = (board<<2) | channel
   wrtbuf = [PRE, CMD_STOPSHORT, dest, short, POST]
   os.write(filehandle,bytes(wrtbuf))   



#
# Set short/hot mode
# set short/hot mode but does NOT touch the end-stops
# Suported only in SW release 2.4 and higher 
#
def set_shorthot(board,channel,short) :
   # if short<SHORT_NONE || short>SHORT_SYST : 
   short_mode[board][channel] = short
   short = short << 4 
   dest = (board<<2) | channel
   wrtbuf = [PRE, CMD_SHORTHOT, dest, short, POST]
   os.write(filehandle,bytes(wrtbuf))   

#
# Set brushed ramps
#
def set_brush_ramps(board,channel,ramp_up,ramp_down,ramp_halt) :
   #GB_CHECK(board>=0   && board<=3,  "set_ramps illegal board\n")
   #GB_CHECK(channel>=0 && channel<=3,"set_ramps illegal channel\n")
   #GB_CHECK(ramp_up>=GB_RAMP_NONE && ramp_up<=GB_RAMP_700,"set_ramps illegal ramp up\n")
   #GB_CHECK(ramp_up>=GB_RAMP_NONE && ramp_up<=GB_RAMP_700,"set_ramps illegal ramp down\n")
   #GB_CHECK(ramp_up>=GB_RAMP_NONE && ramp_up<=GB_RAMP_700,"set_ramps illegal ramp halt\n")
   arg1 = ramp_up | (ramp_down<<4)
   arg2 = ramp_halt
   dest = (board<<2) | channel
   wrtbuf = [PRE, CMD_STOPSHORT, dest, arg1, arg2, POST]
   os.write(filehandle,bytes(wrtbuf))   


# Brushed movement
# board   0..3
# channel 0..3
# direction 0=stop
#           1=A
#           2=B
# ramp = 0..15 off,.. 5 seconds
def move_brushed(board,channel,direction) :
   # To do : check the arguments
   dest = (board<<2) | channel
   wrtbuf = [PRE, CMD_LINON, dest, direction, POST]
   os.write(filehandle,bytes(wrtbuf))
 
 
# Brushed frequency and duty-cycle
# board   0..3
# channel 0..3
# Frequency 10-10000
# duty-cycle 0.0 .. 100.0 (0.1 accurate)
def pwm_brushed(board,channel,freq,dc) :
   # To do : check the arguments
   dest = (board<<2) | channel
   i = int(freq+0.5) # to integer! 
   freq_ms = (i>>8) & 0x0FF
   freq_ls = i & 0x0FF
   wrtbuf = [PRE, CMD_LINFREQ, dest, freq_ms, freq_ls, POST]
   os.write(filehandle,bytes(wrtbuf))
   i = int(dc*10+0.5) # to integer! 
   dc_ms = (i>>8) & 0x0FF
   dc_ls = i & 0x0FF
   wrtbuf = [PRE, CMD_LINDC, dest, dc_ms, dc_ls, POST]
   os.write(filehandle,bytes(wrtbuf))


# Stepper movement
# board   0..3
# channel 0..3
# Steps -<a lot> .. <+ a lot>
def move_stepper(board,channel,steps) :
  # To do : check the arguments
#  CHECK(board>=0   && board<=3,  "move_stepper illegal board\n")
#  CHECK(channel>=0 && channel<=3,"move_stepper illegal channel\n")
#  CHECK(steps>=-8388608 && steps<=8388607,"move_stepper illegal steps\n")
#  CHECK(motor_mode[board][channel] & MODE_STEP_MASK,"move_stepper not in stepper mode\n")
   dest = (board<<2) | channel
   i = steps & 0x0FFFFFF
   step_ms = (steps >> 16) & 0x0FF
   step_mm = (steps >> 8) & 0x0FF
   step_ls = steps & 0x0FF
   wrtbuf = [PRE, CMD_STEP, dest,step_ms,step_mm,step_ls, POST]
   os.write(filehandle,bytes(wrtbuf))


#
# Stop stepper motor
# 
# Mode is one off:
# STOP_OFF    0  Stop with no power on anchor
# STOP_ON     1  Stop with power on anchor
#
def stop_stepper(board,channel,mode) :
#  To do : check the arguments
#  CHECK(board>=0   && board<=3,  "stop_stepper illegal board\n")
#  CHECK(channel>=0 && channel<=3,"stop_stepper illegal channel\n")
#  CHECK(mode==0 || mode==1,      "stop_stepper illegal mode\n")
#  CHECK(motor_mode[board][channel] & MODE_STEP_MASK,"stop_stepper not in stepper mode\n")
   dest = (board<<2) | channel
   if (mode==STOP_OFF) :
     wrtbuf = [PRE, CMD_LINON, dest, MOVE_STOP, POST]
   else :
     wrtbuf = [PRE, CMD_STEP, dest, 0,0,0, POST]
   os.write(filehandle,bytes(wrtbuf))
 
# Stepper motor frequency
# board   0..3
# channel 0..3
# Frequency 0.0625..5000.0
def freq_stepper(board,channel,freq) :
   # To do : check the arguments
   dest = (board<<2) | channel
   i = int(freq*256 + 0.5)
   freq_ms = (i >> 16) & 0x0FF
   freq_mm = (i >> 8) & 0x0FF
   freq_ls =  i & 0x0FF
   set_step_freq[board][channel] = freq;
   wrtbuf = [PRE, CMD_STEPFREQ, dest, freq_ms, freq_mm, freq_ls, POST]
   os.write(filehandle,bytes(wrtbuf))


#
# Return error status of board
# (zero means no pending errors)
# (-1 means read error)
def read_error_status(board):
   # To do : check the arguments
   dest = board<<2
   wrtbuf = [PRE, CMD_GET_ERROR, dest, POST, POST, POST, POST]
   os.write(filehandle,bytes(wrtbuf))
   termios.tcdrain(filehandle)
   ok , data = read_uart(4)
   if (not ok) : # or wrtbuf[0]!=CMD_GET_ERROR or wrtbuf[1]!=dest) :
     return -1
   val = (data[2]<<8) | data[3]
   return val


MAX_ERROR = 0x0021
error_text  = (
"No error",                                       # 0x0000                        
"Command input buffer overflow",                  # ERROR_INP_OVERFLOW 0x0001 
"Program internal error",                         # ERROR_FATALSYSTEM  0x0002 
"Mode command value error",                       # ERROR_MODEERR      0x0003 
"#Obsolete error code 0x04",                      # 
"Lin. freq error: Motor was not in linear mode",  # ERROR_LINFREQ      0x0005 
"Duty cycle error: Motor was not in linear mode", # ERROR_LINDC        0x0006 
"Illegal linear freq given",                      # ERROR_ILLPWMFREQ   0x0007 
"Illegal duty cycle given",                       # ERROR_ILLPWMDC     0x0008 
"Brushed motor start but not given freq.",        # ERROR_NOLINFREQ    0x0009 
"Stepper motor start but not given freq.",        # ERROR_NOSTEPFREQ   0x000A 
"Step command: Motor was not in step mode",       # ERROR_STEP         0x000B 
"Step freq. command: Motor was not in step mode", # ERROR_STEPFREQ     0x000C 
"#Obsolete error code 0x0D",                      # 
"#Obsolete error code 0x0E",                      # 
"#Obsolete error code 0x0F",                      # 
"Start command given with halt active",           # ERROR_HALTACTIVE   0x0010 
"Timer queue pool empty",                         # ERROR_TQ_EMPTY     0x0011 
"Serial output queue overflow",                   # ERROR_SEROUTOVFL   0x0012 
"Illegal stepper frequency",                      # ERROR_ILLSTEPFREQ  0x0013 
"Write to DAC which is disabled",                 # ERROR_DACDIS       0x0014 
"Read from ADC which is disabled",                # ERROR_ADCDIS       0x0015 
"Enable ADC illegal mask bits",                   # ERROR_ADCMASK      0x0016 
"Enable DAC illegal mask bits",                   # ERROR_DACMASK      0x0017 
"Linear on/off direction but not a lin. motor",   # ERROR_LINON        0x0018 
"Illegal command",                                # ERROR_ILLCOMMAND   0x0019 
"HALT was active",                                # ERROR_HALTSEEN     0x001A 
"Enable 0 was negated",                           # ERROR_A_SEEN       0x001B 
"Enable 1 was negated",                           # ERROR_B_SEEN       0x001C 
"Enable 2 was negated",                           # ERROR_C_SEEN       0x001D 
"Enable 3 was negated",                           # ERROR_D_SEEN       0x001E 
"DCC message queue overflow",                     # ERROR_DCC_OVFL     0x001F 
"DCC illegal message (length)",                   # ERROR_DCC_MESS     0x0020 
"Illegal error status code"  )

def error_string(error_number):
  if (error_number<0 or error_number>MAX_ERROR):
    error_number = MAX_ERROR
  return error_text[error_number]


#
# Get motor configuration from board
#
# Returns a list with 8 integers
# [0] = operating mode 
# [1] = endstop mode, 4 bits
#        0x01: A set, 0x02: B set
#        0x04: A High 0x08: B high
# [2] = short mode 
# [3] = frequency in integer format
#       brushed motors: integer =freq
#       stepper motors: integer =freq*256
# [4] = duty_cycle  (ignore for steppers)
# [5] = ramp up     (ignore for steppers)
# [6] = ramp down   (ignore for steppers)
# [7] = ramp halt   (ignore for steppers)
#
# returns empty list on fail 
#
#
# command returns 13 bytes:
# ID, CMD, mode, endstop+short,
# freq:MS, freq:MM, freq:LS,
# duty-cycle:MS, duty-cycle:LS,
# Ramp-up+Ramp-down,  Ramp-halt,
# 0, 0
def get_motor_config(brd,mot) :
   id = (brd<<2) | mot
   wrtbuf = [PRE, CMD_MOT_CONFIG, id, POST, POST, POST, POST, POST,
             POST, POST, POST, POST, POST, POST, POST, POST]
   os.write(filehandle,bytes(wrtbuf))
   termios.tcdrain(filehandle)
   ok , rec_data = read_uart(13)
   if (not ok) : # or rec_data[0]!=CMD_MOT_CONFIG or rec_data[1]!=dest) :
      return []
   motor_data = [0]*8
   motor_data[0] = rec_data[2] & 0x1F
   motor_data[1] = rec_data[3] & 0xF
   motor_data[2] = rec_data[3]>>4
   motor_data[3] =(rec_data[4]<<16) + (rec_data[5]<<8)+rec_data[6]
   motor_data[4] =(rec_data[7]<<8)  + rec_data[8]
   motor_data[5] =(rec_data[9] & 0x0F)
   motor_data[6] =(rec_data[9] >>4)
   motor_data[7] =(rec_data[10] & 0x0F)
   return motor_data
 
#
# Get motor status from board
#
# Returns a list with 2 integers
# [0] = movement (direction/stop)
# [1] = number of steps still to take 
#
# returns empty list on fail 
#
#
def get_motor_status(brd,mot) :
   id = (brd<<2) | mot
   wrtbuf = [PRE, CMD_MOT_STATUS, id, POST, POST, POST, POST, POST, POST]
   os.write(filehandle,bytes(wrtbuf))
   # returns 6 bytes:
   # ID, CMD, move,
   # step_count:MS, step_count:MM, step_count:LS
   termios.tcdrain(filehandle)
   ok , rec_data = read_uart(6)
   if (not ok) : # or rec_data[0]!=CMD_MOT_STATUS or rec_data[1]!=dest) :
      return []
   motor_data = [0]*2
   motor_data[0] = rec_data[2] & 0x0F
   motor_data[1] =(rec_data[3]<<16) + (rec_data[4]<<8)+rec_data[5]
   return motor_data 

#
# Get motor missed steps from board
#
# return list with on element: missed steps
# returns empty list on fail 
#
def get_motor_missed(brd,mot) :
   id = (brd<<2) | mot
   wrtbuf = [PRE, CMD_MOT_MISSED, id, POST, POST, POST, POST, POST, POST]
   os.write(filehandle,bytes(wrtbuf))
   # returns 8 bytes:
   # ID, CMD,
   # missed:MS, missed:MM, missed:LS
   # three times 0 
   termios.tcdrain(filehandle)
   ok , rec_data = read_uart(8)
   if (not ok) : # or rec_data[0]!=CMD_MOT_MISSED or rec_data[1]!=dest) :
      return []
   motor_data = [0]*2
   motor_data[0] =(rec_data[2]<<16) + (rec_data[3]<<8)+rec_data[4]
   # Next should be zero 
   motor_data[1] =(rec_data[5]<<16) + (rec_data[6]<<8)+rec_data[7]
   return motor_data 


#
# Send DCC message 
# Board is the usual 0-3
# channel is special here
# The LS 4 bits indicate to which channel(s) to send
#  bin hex  dec
# 0001  01   1 -> send to chan. 0
# 0010  02   2 -> send to chan. 1
# 0100  04   4 -> send to chan. 2
# 1000  08   8 -> send to chan. 3
# e.g. 
# 1010  0A  10 -> send to chan. 0 & 2
#
# The DCC check byte is not send!
#
def send_dcc_mess(board,channel,data) :
#  GB_CHECK(board>=0  && board<=3,   "send_dcc_cmnd illegal board\n")
#  GB_CHECK(channel>0 && channel<=15,"send_dcc_cmnd illegal channel set\n")
   l = len(data)
   if l<2 or l>5 :
      raise MyException("illegal DCC message size") 
   wrtbuf = [0]*10
   dest   = board<<2
   info  = (channel<<4) | l
   wrtbuf[0] = PRE
   wrtbuf[1] = CMD_DCC_MESS
   wrtbuf[2] = dest
   wrtbuf[3] = info
   for b in range (0,5) :
      if b<l :
         wrtbuf[4+b] = data[b]
      else :
         wrtbuf[4+b] = 0
   wrtbuf[9] = POST
   os.write(filehandle,bytes(wrtbuf))


#
# DCC configure
# This routine does NOT support the 'no idle' flag
#
# preamble and repeat are set per board, not per channel
# dc is not very well supported and the  use is generaly discouraged
#
# 19-Oct-2014 : This function is NOT tested!
# 
def dcc_config(board,channel,repeat,preamble,dc) :
   #GB_CHECK(board>=0  && board<=3,   "dcc_config illegal board\n")
   #GB_CHECK(channel>=0 && channel<=3,"dcc_config illegal channel\n")
   #GB_CHECK(repeat>=4 && repeat<=255,"dcc_config illegal repeat\n")
   #GB_CHECK(preamble>=14 && preamble<=255,"dcc_config illegal preamble\n")
   #GB_CHECK(dc>=-100 && dc<=100,"dcc_config illegal dc\n")
   id = board<<2 | channel
   no_idle = 0 # set to 1 only for testing, debug & development 
   wrtbuf = [PRE, CMD_DCC_CONFIG, id, repeat, preamble, dc, no_idle, POST ]
   os.write(filehandle,bytes(wrtbuf))
 

# Stepper ramping
#  CHECK(board>=0   && board<=3,  "move_stepper illegal board\n")
#  CHECK(channel>=0 && channel<=3,"move_stepper illegal channel\n")
#  CHECK(start>=-8388608 && steps<=8388607,"move_stepper illegal steps\n")
#  CHECK(motor_mode[board][channel] & MODE_STEP_MASK,"move_stepper not in stepper mode\n")
def ramp_stepper(board,channel,start_stop,ramprate) :
# Error of not setting the freq is high so DO check that
   id = board<<2 | channel
   if set_step_freq[board][channel]==0 :
      raise MyException("stepper freq must be set before step ramping") 
   dest = (board<<2) | channel
   i = int(start_stop*256 + 0.5)
   ss_ms = (i >> 16) & 0x0FF
   ss_mm = (i >> 8) & 0x0FF
   ss_ls =  i & 0x0FF
   if ramprate>set_step_freq[board][channel]/10.0 :
      raise MyException("step ramping rate must be <=10% of freq")       
   i = int(ramprate*256 + 0.5)
   rate_ms = (i >> 16) & 0x0FF
   rate_mm = (i >> 8) & 0x0FF
   rate_ls =  i & 0x0FF
   wrtbuf = [PRE, CMD_STEPRAMP, id, ss_ms, ss_mm,ss_ls, rate_ms, rate_mm, rate_ls,POST]
   show_buf("ramp",wrtbuf)
   os.write(filehandle,bytes(wrtbuf)) 
 
#********************************************\
#**                                        **
#**    BBB     OOO    AAA   RRR   DDD      **
#**    B  B   O   O  A   A  R  R  D  D     **
#**    BBBB   O   O  AAAAA  RRR   D  D     **
#**    B   B  O   O  A   A  R  R  D  D     **
#**    BBBBB   OOO   A   A  R  R  DDD      **
#**                                        **
#********************************************/

# I use this for testing!   
def send_raw(arg):
  os.write(filehandle,bytes(arg))

#
# Set mode of a J3 pin 
#
def set_pin_mode(board,pin,mode) :
   global pin_mode,end_stop_high
   # To do : check the arguments  
   id = board << 2
   if mode==PIN_SAME :
      return
   pin = pin-1 # range 0-19 
                                          
#  CHECK(board>=0   && board<=3,  "set_pin_mode illegal board\n")
#  CHECK(pin>=1     && pin<=20,   "set_pin_mode illegal pin\n")
#  CHECK(mode>PIN_SAME && mode<=PIN_I2C,"set_pin_mode illegal mode\n")
#  CHECK((pin_modes[pin] & (1<<mode)),"set_pin_mode illegal mode\n")
  
 #
 # Override function code:
 #
   if ( ((pin_mode[board][pin]==PIN_ADC) and (mode!=PIN_ADC)) or \
       ((pin_mode[board][pin]!=PIN_ADC) and (mode==PIN_ADC)) or \
       ((pin_mode[board][pin]==PIN_DAC) and (mode!=PIN_DAC)) or \
       ((pin_mode[board][pin]!=PIN_DAC) and (mode==PIN_DAC)) \
      ) :
      # switch ADC/DAC on/off
      pin_mode[board][pin] = mode  # override old mode 
      
      dac_enb =           (0x01 if pin_mode[board][19]==PIN_DAC else 0x00) # DAC0
      dac_enb = dac_enb | (0x02 if pin_mode[board][17]==PIN_DAC else 0x00) # DAC1
      adc_enb =           (0x01 if pin_mode[board][13]==PIN_ADC else 0x00) # ADC0
      adc_enb = adc_enb | (0x02 if pin_mode[board][12]==PIN_ADC else 0x00) # ADC1
      adc_enb = adc_enb | (0x04 if pin_mode[board][15]==PIN_ADC else 0x00) # ADC2
      adc_enb = adc_enb | (0x08 if pin_mode[board][14]==PIN_ADC else 0x00) # ADC3
      wrtbuf = [PRE, CMD_SETADCDAC, id, adc_enb, dac_enb,POST]
      os.write(filehandle,bytes(wrtbuf))  

   if ((pin_mode[board][pin]==PIN_ENDSTOP) and (mode!=PIN_ENDSTOP) or \
       (pin_mode[board][pin]!=PIN_ENDSTOP) and(mode==PIN_ENDSTOP) \
      ) :
      # switch endmode on/off
      pin_mode[board][pin] = mode # override old mode 
      p = pin & 0x0E
      endstop = 0
      if (pin_mode[board][p+1]==PIN_ENDSTOP):  endstop = endstop | 0x02
      if (pin_mode[board][p]  ==PIN_ENDSTOP):  endstop = endstop | 0x01
      if (end_stop_high[board][p+1]): endstop = endstop | 0x08
      if (end_stop_high[board][p]):   endstop = endstop | 0x04
      id = id | (pin>>1)
      wrtbuf = [PRE, CMD_STOPSHORT, id, endstop,POST]
      os.write(filehandle,bytes(wrtbuf))  
  
   pin_mode[board][pin] = mode # set mode 
   
   # make set-port-to-output-mode command 
   # 0 bit = output, 1 bit = input 
   mask1 = 0xFF # all inputs 
   for p in range (0,8) :
      if (pin_mode[board][p]==PIN_OUTPUT) :
         mask1 = mask1 & ~(1<<p)


   # twiddle bits 12..19
   mask2=0xFF # all inputs 
   if (pin_mode[board][8]==PIN_OUTPUT) :
      mask2 = mask2 & ~0x01
   if (pin_mode[board][9]==PIN_OUTPUT) :
      mask2 = mask2 & ~0x02
   if (pin_mode[board][12]==PIN_OUTPUT) :
      mask2 = mask2 & ~0x04 
   if (pin_mode[board][13]==PIN_OUTPUT) :
      mask2 = mask2 & ~0x08 
   if (pin_mode[board][14]==PIN_OUTPUT) :
      mask2 = mask2 & ~0x10 
   if (pin_mode[board][15]==PIN_OUTPUT) :
      mask2 = mask2 & ~0x20 
   if (pin_mode[board][17]==PIN_OUTPUT) :
      mask2 = mask2 & ~0x40 
   if (pin_mode[board][19]==PIN_OUTPUT) :
      mask2 = mask2 & ~0x80 
   wrtbuf = [PRE, CMD_SETIO, id, 0xFF, mask2, mask1,POST]
   os.write(filehandle,bytes(wrtbuf))  


#
# Set mode of all J3 pins
#
def set_allpins_mode(board,modes) :
   global pin_mode,end_stop_high
   # To do : check the arguments  
   
   # Check if end modes or DAC/ADC needs changing
   id = board << 2
   adc_dac_change = 0
   endstop_change  = [0,0,0,0]
   for pin in range (0,20) :
      if modes[pin]!=PIN_SAME and \
           not (pin==10 or pin==11 or pin==16 or pin==18 ):
         if ( ((pin_mode[board][pin]==PIN_ADC) and (modes[pin]!=PIN_ADC)) or \
              ((pin_mode[board][pin]!=PIN_ADC) and (modes[pin]==PIN_ADC)) or \
              ((pin_mode[board][pin]==PIN_DAC) and (modes[pin]!=PIN_DAC)) or \
              ((pin_mode[board][pin]!=PIN_DAC) and (modes[pin]==PIN_DAC)) \
            ) :
            adc_dac_change = 1
         
         if ((pin_mode[board][pin]==PIN_ENDSTOP) and (modes[pin]!=PIN_ENDSTOP) or \
             (pin_mode[board][pin]!=PIN_ENDSTOP) and (modes[pin]==PIN_ENDSTOP) \
            ) :
            endstop_change[pin>>1] = 1
         # After checking fill in new mode value 
         pin_mode[board][pin] = modes[pin] 
        
   # Change ADC/DAC settings if required 
   if adc_dac_change!=0 :
      dac_enb =           (0x01 if pin_mode[board][19]==PIN_DAC else 0x00) # DAC0
      dac_enb = dac_enb | (0x02 if pin_mode[board][17]==PIN_DAC else 0x00) # DAC1
      adc_enb =           (0x01 if pin_mode[board][13]==PIN_ADC else 0x00) # ADC0
      adc_enb = adc_enb | (0x02 if pin_mode[board][12]==PIN_ADC else 0x00) # ADC1
      adc_enb = adc_enb | (0x04 if pin_mode[board][15]==PIN_ADC else 0x00) # ADC2
      adc_enb = adc_enb | (0x08 if pin_mode[board][14]==PIN_ADC else 0x00) # ADC3
      wrtbuf = [PRE, CMD_SETADCDAC, id, adc_enb, dac_enb,POST]
      os.write(filehandle,bytes(wrtbuf))  

   # Change endstop settings if required 
   for pin in range (0,4) :
      if endstop_change[pin]!=0 :
         # switch endmode on/off
         id = (board << 2) | pin 
         endstop = 0
         if (pin_mode[board][pin*2+1]==PIN_ENDSTOP):  endstop = endstop | 0x02
         if (pin_mode[board][pin*2]  ==PIN_ENDSTOP):  endstop = endstop | 0x01
         if (end_stop_high[board][pin*2+1]): endstop = endstop | 0x08
         if (end_stop_high[board][pin*2])  : endstop = endstop | 0x04
         wrtbuf = [PRE, CMD_STOPSHORT, id, endstop,POST]
         os.write(filehandle,bytes(wrtbuf))  
 

   # make set-port-to-output-mode command 
   # 0 bit = output, 1 bit = input 
   mask1 = 0xFF # all inputs 
   for p in range (0,8) :
      if (pin_mode[board][p]==PIN_OUTPUT) :
         mask1 = mask1 & ~(1<<p)
   
   # Set output bits 8..15 using mode bits 8,9,12-15,17,19
   mask2=0xFF # all inputs 
   if (pin_mode[board][8]==PIN_OUTPUT) :
      mask2 = mask2 & ~0x01
   if (pin_mode[board][9]==PIN_OUTPUT) :
      mask2 = mask2 & ~0x02
   if (pin_mode[board][12]==PIN_OUTPUT) :
      mask2 = mask2 & ~0x04 
   if (pin_mode[board][13]==PIN_OUTPUT) :
      mask2 = mask2 & ~0x08 
   if (pin_mode[board][14]==PIN_OUTPUT) :
      mask2 = mask2 & ~0x10 
   if (pin_mode[board][15]==PIN_OUTPUT) :
      mask2 = mask2 & ~0x20 
   if (pin_mode[board][17]==PIN_OUTPUT) :
      mask2 = mask2 & ~0x40 
   if (pin_mode[board][19]==PIN_OUTPUT) :
      mask2 = mask2 & ~0x80 
   wrtbuf = [PRE, CMD_SETIO, id, 0xFF, mask2, mask1,POST]
   os.write(filehandle,bytes(wrtbuf))  

#
# Set the output pins in a high/low state
# ALL outputs are set
# The function maps output bits 0..N to all output pins 
# bit  0 : pin 1
# bit  1 : pin 2
# ..
# bit  6 : pin 7
# bit  7 : pin 8
# bit  8 : pin 9   extra0
# bit  9 : pin 10  extra1
# bit 10 : pin 13  ADC1
# bit 11 : pin 14  ADC0
# bit 12 : pin 15  ADC3
# bit 13 : pin 16  ADC2
# bit 14 : pin 18  DAC0
# bit 15 : pin 20  DAC1
# The board will ignore pins which are NOT an output
#
def set_output_pin_state(board,output) :
#  GB_CHECK(board>=0 && board<=3,  "set_output_pin_state illegal board\n")
   # swap bits 14 & 15 
   swap = [0x0000, 0x8000, 0x4000, 0xC000]
   temp = output>>14
   output = (output & 0x3FFF) | swap[temp]
   mask2 = (output >> 8) & 0xFF
   mask1 = output & 0xFF
   wrtbuf = [PRE, CMD_WRITEIO,  board<<2, 0x00, mask2, mask1,POST]
   os.write(filehandle,bytes(wrtbuf))  

   
#
# Activate the open drain outputs
# drain0,drain1 are interpreted as C booleans:
# ==0 means not active
# !=0  means active
# Beware that activate means the pin will go LOW
#
def activate_opendrain(board,drain0,drain1) :
   # GB_CHECK(board>=0 && board<=3,  "activate_opendrain illegal board\n")
   mask = 0
   if drain0!=0 :
      mask = mask | 0x01
   if drain1!=0 :
      mask = mask | 0x02
   wrtbuf = [PRE, CMD_OD, board<<2, mask ,POST]
   os.write(filehandle,bytes(wrtbuf))  
   
                                               
#                                              
# Set a DAC output value                       
# This routine sends a 16-bit value
# which allows future 16-bit DAC's
#
#                                              
def set_dac(board,dac,val) :  
#  GB_CHECK(board>=0 && board<=3, "set_dac illegal board\n") 
#  GB_CHECK(dac>=0 && dac<=1, "set_dac illegal DAC\n") 
#  GB_CHECK(value>=dac_calibrate[board][dac].min && value<=dac_calibrate[board][dac].max, "set_dac illegal value\n") 
   id = (board<<2) | dac 
   # Map value onto 12 bit range
   # calibrate not yet supported
   if (val<DAC_MIN) : val = DAC_MIN
   if (val>DAC_MAX) : val = DAC_MAX
   ivalue = int(((val-DAC_MIN) * 4095.0/(DAC_MAX-DAC_MIN)+0.5)) 
   v_ms = ivalue>>8
   v_ls = ivalue & 0xFF 
   wrtbuf = [PRE, CMD_DAC, id, v_ms, v_ls,POST]
   os.write(filehandle,bytes(wrtbuf))  
                                                
                                                
#                                              
# Read ADC value                               
#                                              
# a return value of -1 indicates an error      
#                                              
def read_adc(board,adc) :            
   # To do : check the arguments
   dest = (board<<2) | adc
   wrtbuf = [PRE, CMD_GET_ADC, dest, POST, POST, POST, POST]
   os.write(filehandle,bytes(wrtbuf))
   termios.tcdrain(filehandle)
   ok , data = read_uart(4)
   if (not ok) : # or data[0]!=CMD_GET_ERROR or data[1]!=dest) :
      return -1
   ival = (data[2]<<8) | data[3]
   ## convert integer to float in range 0..3.3V
   return ival*(3.3/4095.0)

#
# Read inputs
#
# return -1 (0xFFFFFF) on error
# return input values otherwise 
# Return value is in range 0x000..0x0FFFF
# 
def read_inputs(board) :
#  GB_CHECKN(board>=0 && board<=3, "read_inputs illegal board\n")
   dest = (board << 2)
   wrtbuf = [PRE, CMD_READIO, dest, POST, POST, POST, POST, POST]
   os.write(filehandle,bytes(wrtbuf))
   termios.tcdrain(filehandle)
   ok , rec_data = read_uart(5)
   if (not ok) : # or data[0]!=CMD_GET_ADC or data[1]!=dest) :
      return -1
   i_value  = rec_data[4]
   i_value |= rec_data[3]<<8
   i_value |= rec_data[2]<<16
   return i_value



#
# Read board I/O status
#
# Returns a list of 20 element one for each pin
# On error returns an empty list
# return 1: read succesfull
#
# Note: the internal pin status is also updated
#
def get_io_setup(brd) :
   #GB_CHECK(brd>=0 && brd<=3,  "get_io_status illegal board\n");
   id = brd<<2
   tx = [0]*20
   tx[0] = PRE
   tx[1] = CMD_IO_STATUS
   tx[2] = id
   for i in range(3,19) : 
      tx[i] = POST;
   os.write(filehandle,bytes(tx))
   termios.tcdrain(filehandle)
  
   # Read input/output status
   # return is:
   #  - ID, CMD            (2 bytes)  0, 1
   #  - adc_enable     3-0 (1 byte)   2
   #  - dac_enable     1-0 (1 byte)   3
   #  - inputs pins   23-0 (3 bytes)  4, 5, 6
   #  - output pins   23-0 (3 bytes)  7, 8, 9
   #  - output status 23-0 (3 bytes) 10,11,12
   #  - open drain status (1 unsigned char)   13
   #  - unused (2 bytes)             14,15
   # Total 16 bytes
   ok , rec_data = read_uart(16)
   if (not ok) : # or rec_data[0]!=CMD_IO_STATUS or rec_data[1]!=dest) :
      status = []
      return status

   # EXT
   for i in range(0,8) : 
      if (rec_data[6] & (1<<i)) : 
         pin_mode[brd][i^1] = PIN_INPUT
      else : 
         if (rec_data[9] & (1<<i)) : 
            pin_mode[brd][i^1] = PIN_OUTPUT
         else : # not input or output must be endstop
            pin_mode[brd][i^1] = PIN_ENDSTOP
   
   # Spares
   for i in range(0,2) : 
      if (rec_data[5] & (1<<i)) :
         pin_mode[brd][i^1+8] = PIN_INPUT
      else :
         pin_mode[brd][i^1+8] = PIN_OUTPUT
      # to do : I2C mode 
   
   # ADCs
   for i in range(0,4) : 
      if (rec_data[2] & (1<<i)) :
        pin_mode[brd][i^1+12] = PIN_ADC
      else :
         if (rec_data[5] & (0x04<<i)) :
            pin_mode[brd][i^1+12] = PIN_INPUT
         else :
            pin_mode[brd][i^1+12] = PIN_OUTPUT
   
   # DACs
   if (rec_data[3] & (0x02)) : # DAC1
      pin_mode[brd][17] = PIN_DAC
   else :
      if (rec_data[5] & 0x40) :
         pin_mode[brd][17] = PIN_INPUT
      else :
         pin_mode[brd][17] = PIN_OUTPUT
   
   if (rec_data[3] & (0x01)) : # DAC0
      pin_mode[brd][19] = PIN_DAC
   else :
      if (rec_data[5] & 0x80) :
         pin_mode[brd][19] = PIN_INPUT
      else :
         pin_mode[brd][19] = PIN_OUTPUT
         
   # gather up all pins and return in list 
   status = [0]*20
   for i in range(0,20) :
      status[i] = pin_mode[brd][i]
       
   return status

#
# Set baudrate of Gertbot
# Then change local baudrate
# 23/04/2015 
# For an yet unknown reason baudrates 230K and 
# 19.2K do not work with PI
# This DOES work between the gertbot and a USB serial port
# Assuming somewhere a baudrate accuracy error
def set_baudrate(baud) :
   if (baud==0 or baud==4) :
    return 0
   tx = [0]*20
   tx[0] = PRE
   tx[1] = CMD_SETBAUD
   tx[2] = 0x18
   tx[3] = 0x81
   tx[4] = baud
   tx[5] = POST
   os.write(filehandle,bytes(tx))   
   termios.tcdrain(filehandle)
   # add delay to allow not only queue but also
   # peripheral shift register to drain 
   time.sleep(0.1)
   port_attr = termios.tcgetattr(filehandle)
   if baud==0 :
      port_attr[4] = termios.B19200
      port_attr[5] = termios.B19200
   if baud==1 :
      port_attr[4] = termios.B38400
      port_attr[5] = termios.B38400
   if baud==2 :
      port_attr[4] = termios.B57600
      port_attr[5] = termios.B57600
   if baud==3 :
      port_attr[4] = termios.B115200
      port_attr[5] = termios.B115200
   if baud==4 :
      port_attr[4] = termios.B230400
      port_attr[5] = termios.B230400
   termios.tcsetattr(filehandle,termios.TCSANOW,port_attr)
   time.sleep(0.5)
   


#****************************************#
#*                                      *#
#* Q u a d r a t u r e   e n c o d e r  *#
#*                                      *#
#****************************************#

# Quadrature encoder on/off
def quad_on(board,channel,on,position,rev): 
#  GB_CHECK(board>=0  && board<=3,   "quad_on illegal board\n");
#  GB_CHECK(channel>=0 && channel<=3,"quad_on illegal channel\n");
#  GB_CHECK(position>=-0x07FFFFF && position<=0x07FFFFF,"quad_on illegal position\n");
#  GB_CHECK(gb_motor[board][channel].mode==GB_MODE_BRUSH,"quad_on not in brushed mode\n");
   dest  = (board<<2) | channel 
   if on!=0 : flags = QUAD_ON 
   else : flags=0
   if rev!=0 : flags = flags | QUAD_REVERSE 
   pos_ms = (position >> 16) & 0x0FF
   pos_mm = (position >> 8) & 0x0FF
   pos_ls =  position & 0x0FF
   wrtbuf = [PRE, CMD_QUAD, dest,flags,pos_ms,pos_mm,pos_ls,POST]
   os.write(filehandle,bytes(wrtbuf))


# Quadrature encoder read
# returns tupple (two ints)
def quad_read(board,channel) :
#  GB_CHECK(board>=0  && board<=3,   "quad_read illegal board\n");
#  GB_CHECK(gb_motor[board][channel].flags&QUAD_ON,"quad_read not in quadrature mode\n");
   dest = (board<<2) | channel;
   wrtbuf = [PRE,CMD_QUAD_READ,dest,POST,POST,POST,POST,POST,POST,POST,POST]
   os.write(filehandle,bytes(wrtbuf))
   termios.tcdrain(filehandle)   
   ok , data = read_uart(7) # id cmd pos pos pos err err 
   if (not ok) : # or wrtbuf[0]!=CMD_GET_ERROR or wrtbuf[1]!=dest) :
     return -1, -1
   pos = (data[2]<<16) | (data[3]<<8) | data[4]
   # sign extend from 24 to 32 bit 
   # python is very bad at typing. This does not work:
   #if pos & 0x00800000 : pos = int(pos | 0xFF000000)
   if pos & 0x00800000 :  
      pos = int((pos|0xFF000000)-0x100000000)
   err = (data[5]<<8) | data[6]
   return pos,err
 
# Quadrature encoder goto
def quad_goto(board,channel,position,duty_cycle):   
#  GB_CHECK(board>=0  && board<=3,   "quad_on illegal board\n");
#  GB_CHECK(channel>=0 && channel<=3,"quad_on illegal channel\n");
#  GB_CHECK(gb_motor[board][channel].flags&QUAD_ON,"quad_goto not in quadrature mode\n");
#  GB_CHECK(position>=-0x07FFFFF && position<=0x07FFFFF,"quad_on illegal position\n");
#  GB_CHECK(duty_cycle>=0.0 && duty_cycle<=100.0,"quad_goto illegal duty_cycle\n");
   dest = (board<<2) | channel;
   pos_ms = (position >> 16) & 0x0FF
   pos_mm = (position >> 8) & 0x0FF
   pos_ls =  position & 0x0FF
   i = int(duty_cycle*10+0.5) # to integer! 
   dc_ms = (i>>8) & 0x0FF
   dc_ls = i & 0x0FF
   wrtbuf = [PRE, CMD_QUAD_GOTO, dest, pos_ms, pos_mm, pos_ls, dc_ms, dc_ls,POST]
   os.write(filehandle,bytes(wrtbuf))


# Quadrature encoder limit & slow settings
def quad_limit(board,channel,max_on,min_on,slow_on,maxp,minp,slow_dist,slow_dc) :
#  GB_CHECK(board>=0  && board<=3,   "quad_slow illegal board\n");
#  GB_CHECK(channel>=0 && channel<=3,"quad_slow illegal channel\n");
#  GB_CHECK(gb_motor[board][channel].flags&QUAD_ON,"quad_slow not in quadrature mode\n");
#  GB_CHECK(maxp>=-0x07FFFFF && maxp<=0x07FFFFF,"quad_slow illegal maxp. position\n");
#  GB_CHECK(minp>=-0x07FFFFF && minp<=0x07FFFFF,"quad_slow illegal minp. position\n");
#  GB_CHECK(slow_dist>=0 && slow_dist<=0xFFFF,"quad_slow illegal slow distance\n");
#  GB_CHECK(slow_dc>=0.0 && slow_dc<=100.0,"quad_slow illegal duty_cycle\n");
   dest = (board<<2) | channel;
   flags = 0;
   if max_on!=0 : flags = flags | QUAD_TOP
   if min_on!=0 : flags = flags | QUAD_BOT
   if slow_on!=0: flags = flags | QUAD_GOSLOW
   max_ms = (maxp >> 16) & 0x0FF
   max_mm = (maxp >> 8) & 0x0FF
   max_ls =  maxp & 0x0FF
   min_ms = (minp >> 16) & 0x0FF
   min_mm = (minp >> 8) & 0x0FF
   min_ls =  minp & 0x0FF
   slow_dist_ms = (slow_dist >> 8) & 0x0FF
   slow_dist_ls =  slow_dist & 0x0FF
   i = int(slow_dc*10+0.5) # to integer! 
   dc_ms = (i>>8) & 0x0FF
   dc_ls = i & 0x0FF
   wrtbuf = [PRE,CMD_QUAD_LIMIT,dest,flags,max_ms,max_mm,max_ls,min_ms,min_mm,min_ls,slow_dist_ms,slow_dist_ls,dc_ms,dc_ls,POST]
   os.write(filehandle,bytes(wrtbuf))

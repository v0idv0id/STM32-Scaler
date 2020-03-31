#!/usr/bin/env python3

# MIT License
# Copyright (c) 2020 v0idv0id - Martin Willner - lvslinux@gmail.com

import getopt, sys, itertools

bit="16"
TIM_BASE_CLOCK=84000000
TARGET_F = 42000000
error=0.0
max_results=-1
DUTY=50.0

cmd_args = sys.argv
arg_list = cmd_args[1:]
soptions="hb:c:e:f:m:t:d:"
loptions=["help","bits=","clk=","error=","freq=","max=","time=","duty="]
spinner = itertools.cycle(['-', '/', '|', '\\'])


try:
    arguments, values = getopt.getopt(arg_list,soptions,loptions)
except getopt.error as err:
    print(str(err))
    sys.exit(2)

for current_argument, current_value in arguments:
    if current_argument in  ("-b","--bits"):
        bit=str(current_value)
    elif current_argument in ("-c","--clk"):
        TIM_BASE_CLOCK=int(current_value)
    elif current_argument in ("-e","--error"):
        error=float(current_value)
    elif current_argument in ("-f","--freq"):
        TARGET_F=float(current_value)
    elif current_argument in ("-t","--time"):
        TARGET_F=float(1.0/float(current_value))
    elif current_argument in ("-d","--duty"):
        DUTY=float(current_value)
    elif current_argument in ("-h","--help"):
        print("-f VALUE --freq=VALUE : Calculte ARR and PSC for this FRQUENCY [Hz]!")
        print("or")
        print("-t VALUE --time=VALUE : Calculte ARR and PSC event inteval [s]!")
        print("")
        print("-b VALUE --bits=VALUE : 16 or 32 - timer type")
        print("-c VALUE --clk=VALUE : Timer base clock in [Hz]")
        print("-e VALUE --error=VALUE : Accepted error in [%]")
        print("-d VALUE --duty=VALUE : Calculate the CRRx value for this duty cycle [%]")




        quit()
    elif current_argument in ("-m","--max"):
        max_results=int(current_value)

TARGET_ARR_MAX = { "8": 2**8-1, "16": 2**16-1, "32": 2**32-1 }
TARGET_PSC_MAX= { "16": 2**16-1 }
TARGET_PSC=0
TARGET_ARR=0



TARGET_UPDATE_F_MAX = TIM_BASE_CLOCK / ((TARGET_PSC + 1)*(TARGET_ARR+1))
TARGET_UPDATE_F_MIN = TIM_BASE_CLOCK / ((TARGET_PSC_MAX["16"] + 1)*(TARGET_ARR_MAX[bit]+1))


print("*** BIT MODE:",bit)
print("*** BASE_CLK:",TIM_BASE_CLOCK, "[Hz]")
print("*** TARGET_FREQUENCY:",TARGET_F, "[Hz]")
print("*** ERROR:",error,"[%]")
print("*** DUTY:",DUTY,"[%]")

print("**> MAX:",TARGET_UPDATE_F_MAX," [Hz]") 
#, "[1/s]\n", secondlist( 1/TARGET_UPDATE_F_MAX))
print("**> MIN:",TARGET_UPDATE_F_MIN," [Hz]")  
#, "[1/s]\n",secondlist(1/TARGET_UPDATE_F_MIN))

if TARGET_F > TARGET_UPDATE_F_MAX or  TARGET_F < TARGET_UPDATE_F_MIN:
    print("Target frequency is not in range of MIN/MAX!")
    quit()

results = []

def search_arr_psc():
    right = TIM_BASE_CLOCK / TARGET_F
    # right=int(right)
    print("(arr+1)*(psc+1) = TIM_BASE_CLOCK / TARGET_F")
    print("(arr+1)*(psc+1) =", TIM_BASE_CLOCK, "/", TARGET_F)
    print("(arr+1)*(psc+1) =",right)
    if TIM_BASE_CLOCK % TARGET_F != 0:
        print("\nSOLUTION WITHOUT ERROR NOT POSSIBLE - TIM_BASE_CLOCK / TARGET_F is not integer")
        if error == 0:
            print("You must use an --error= value >0 for this frequency!")
            quit()
    print( "Calculate...")
    for psc in range(0,TARGET_PSC_MAX["16"]+1):
        sys.stdout.write(next(spinner))
        sys.stdout.flush()
        x = (TIM_BASE_CLOCK / (TARGET_F * (psc+1))) -1 
        if TIM_BASE_CLOCK  % (psc+1) == 0 and x <= TARGET_ARR_MAX[bit]:
            for arr in range(0,TARGET_ARR_MAX[bit]+1):
                left = (arr+1)*(psc+1) 
                pererror = abs((1- (TARGET_F / (TIM_BASE_CLOCK/left)))*100)
                if pererror <= error:
                    freq = TIM_BASE_CLOCK/left
                    d = int(arr/(100.0/DUTY))
                    results.append({"psc":psc,"arr":arr,"left":left,"freq":freq,"pererror":pererror,"delta":abs(freq-TARGET_F),"duty":d})
        sys.stdout.write('\b')    

def secondlist(x):
    s = x
    ms = x*(10**3)
    us = x*(10**6)
    ns = x*(10**9)
    ps = x*(10**12)
    fs = x*(10**15)
    return {"s":s, "ms":ms, "µs":us, "ns":ns, "ps":ps, "fs":fs}




search_arr_psc()

if error != 0:
    result_sorted = sorted(results, key = lambda i: (i['pererror']))
else:
    result_sorted = sorted(results, key = lambda i: (i['psc']))

j=0
for i in result_sorted:
    if j == max_results:
        quit()
    print("PSC:",i["psc"],"ARR:",i["arr"]," => FREQ:",i["freq"],"[Hz]","ERROR:",i["pererror"],"[%] - CRRx[",DUTY,"%]:",i["duty"])
    j+=1
print (j,"Results. Reduce with --max=")
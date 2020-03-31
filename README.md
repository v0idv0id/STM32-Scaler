# STM-SCALER a simple PSC, ARR and CCRx calculator


## Usage timescale.py
```
./timscale.py --help

-f VALUE --freq=VALUE : Calculte ARR and PSC for this FRQUENCY [Hz]!
or
-t VALUE --time=VALUE : Calculte ARR and PSC event inteval [s]!

-b VALUE --bits=VALUE : 16 or 32 - timer type
-c VALUE --clk=VALUE : Timer base clock in [Hz]
-e VALUE --error=VALUE : Accepted error in [%]
-d VALUE --duty=VALUE : Calculate the CRRx value for this duty cycle [%]
```

If no arguments are given the default values are used. The default values can be seen when starting the program without any arguments.

### Example

Finding the first 5 solutions for a Timer Event frequency of 1250 Hz. In addition the CRRx for a duty cycle of 12.5% are calculated. Timer base clock is 84Mhz

```
./timscale.py --freq 1250 --max=5 --duty=12.5
*** BIT MODE: 16
*** BASE_CLK: 84000000 [Hz]
*** TARGET_FREQUENCY: 1250.0 [Hz]
*** ERROR: 0.0 [%]
*** DUTY: 12.5 [%]
**> MAX: 84000000.0  [Hz]
**> MIN: 0.01955777406692505  [Hz]
(arr+1)*(psc+1) = TIM_BASE_CLOCK / TARGET_F
(arr+1)*(psc+1) = 84000000 / 1250.0
(arr+1)*(psc+1) = 67200.0
Calculate...
PSC: 1 ARR: 33599  => FREQ: 1250.0 [Hz] ERROR: 0.0 [%] - CRRx[ 12.5 %]: 4199
PSC: 2 ARR: 22399  => FREQ: 1250.0 [Hz] ERROR: 0.0 [%] - CRRx[ 12.5 %]: 2799
PSC: 3 ARR: 16799  => FREQ: 1250.0 [Hz] ERROR: 0.0 [%] - CRRx[ 12.5 %]: 2099
PSC: 4 ARR: 13439  => FREQ: 1250.0 [Hz] ERROR: 0.0 [%] - CRRx[ 12.5 %]: 1679
PSC: 5 ARR: 11199  => FREQ: 1250.0 [Hz] ERROR: 0.0 [%] - CRRx[ 12.5 %]: 1399
```

## The problem & solution

For a time based interrupt using the internal clock of a timer finding the right PSC and ARR values for a given interrupt interval (or frequency) can be quite difficult. 

Since ```EVENT_FREQUENCY = TIM_CLK / ( (PSC+1) * (ARR+1) )``` finding the correct ```PSC``` and ```ARR``` values for a given EVENT_FREQUENCY is solving the equation:

```(PSC+1) * (ARR+1) = TIM_CLK / EVENT_FREQUENCY = FREQ_RATIO```

To solve this equation in a "smart" way we can make some assumtions:

* If the ```FREQ_RATIO``` is not integer ```(TIM_CLK modulo FREQ_RATIO) != 0 ``` it is not possible to find a solution for ```PSC``` and ```ARR```. In this case a small error must be accepted. 

  * AND for any given integer ```PSC``` the solution of: ``` ARR = (TIM_BASE_CLOCK / (TARGET_F * (PSC+1))) -1 ``` must also be integer. So ``` TIM_BASE_CLOCK modulo (PSC+1) == 0``` in order to make ```ARR``` as an integer possible. 
  * AND ARR must be smaler that the maximum of 16-bit: 65535

Since ```PSC``` and ```ARR``` do have different functionality (ARR is i.e. the range/granularity in which the PWM duty cycle ```CCRx``` can be set) its important to have all possible set of ```PSC``` and ```ARR``` to choose from.

The program gives a list of all possibilities for PSC and ARR.


## SMT32 background and timers

### Time base generator

Depending on the clock (TIM_CLK), prescaler (PSC) and auto reload (ARR), repetition counter (RCR)  parameters, the 16-bit or 32-bit timer can generate an update event from a nanosecond to a few minutes or wider.

* TIM_CLK in Hz [1/s] 
* ETR_CLK in Hz - The external clock frequency connected to ETR pin.
* TIx_CLK in Hz - The external clock frequency connected to TI1 pin or TI2 pin.
* ITRx_CLK in Hz - The internal trigger frequency mapped to timer trigger input (TRGI)
* ETR_PSC - External trigger prescaler starting with 1
* PSC - 16-bit value [0:65535] = [0:2^16-1]
* ARR - 16-bit value [0:65535] or 32-bit value [0:4294967295] = [0:2^32-1]
* RCR - 16-bit value [0:65535] = [0:2^16-1]
* EVENT_FREQUENCY in Hz [1/s] between TIM_CLK (max value) and TIM_CLK/(2^16-1)^3 (with RCR) or TIM_CLK/(2^16-1)^2

#### Internal clock   
EVENT_FREQUENCY = TIM_CLK / ( (PSC+1) * (ARR+1) * (RCR + 1))

#### External mode1 (TI1 or TI2 pins)
EVENT_FREQUENCY = ITIx_CLK / ( (PSC+1) * (ARR+1) * (RCR + 1))

#### External clock mode2 (ETR pin)
EVENT_FREQUENCY = ETR_CLK / ( (ETR_PSC) * (PSC+1) * (ARR+1) * (RCR + 1))

#### Internal trigger clock (ITRx)
EVENT_FREQUENCY = ITRx_CLK / ( (PSC+1) * (ARR+1) * (RCR + 1))

#### Example - Internal clock
* TIM_CLK = 84MHz = 84000000 Hz
* PSC = 1
* ARR = 104
* RCR = 0

EVENT_FREQUENCY = 84000000 / ( (1 + 1) * (104 + 1) * (0 + 1)) = 400000 Hz 

## References
* https://www.st.com/resource/en/application_note/dm00042534-stm32-crossseries-timer-overview-stmicroelectronics.pdf
* https://www.st.com/resource/en/application_note/dm00236305-generalpurpose-timer-cookbook-for-stm32-microcontrollers-stmicroelectronics.pdf
## License and Author

MIT License - Copyright (c) 2020 v0idv0id - Martin Willner - lvslinux@gmail.com

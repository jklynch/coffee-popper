import RPi.GPIO as GPIO

from adafruit_motorkit import MotorKit

import board
import busio
import digitalio
import adafruit_max31856


class CoffeePopper:
    def __init__(self):
        print('GPIO mode: {}'.format(GPIO.getmode()))
        # something is setting GPIO mode to BCM before we get here
        # assume mode is BCM
        ##GPIO.setmode(GPIO.BOARD)
        ##heater_pwm_pin = 12
        heater_pwm_pin = 18
        GPIO.setup(heater_pwm_pin, GPIO.OUT)
        heater_pwm_frequency = 100.0
        self.heater = GPIO.PWM(heater_pwm_pin, heater_pwm_frequency)
        heater_pwm_duty_cycle = 25.0

        kit = MotorKit()
        self.fan = kit.motor1

        spi = busio.SPI(board.SCK, board.MOSI, board.MISO)
        cs = digitalio.DigitalInOut(board.D5)
        cs.direction = digitalio.Direction.OUTPUT
        self.thermocouple = adafruit_max31856.MAX31856(spi, cs)

    def cleanup(self):
        self.heater.stop()
        GPIO.cleanup()

        self.fan.throttle = None

    def control_heater(self, duty_cycle):
        print('heater duty cycle: {:.5f}'.format(duty_cycle))
        self.heater.start(duty_cycle)

    def control_fan(self, throttle):
        print('fan throttle: {:.5f}'.format(throttle))
        self.fan.throttle = throttle

    def read_temperature(self):
        print('thermocouple temperature: {:.5f}'.format(self.thermocouple.tempeature))



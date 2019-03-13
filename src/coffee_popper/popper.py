import json
import random
import time

import zmq


class TestPopper:
    def __init__(self):
        random.seed(1)
        self.heater_duty_cycle = 0.0
        self.fan_throttle = 0.0

    def cleanup(self):
        print('cleaning up')

    def control_heater(self, duty_cycle):
        self.heater_duty_cycle = duty_cycle
        print('heater duty cycle: {:.5f}'.format(duty_cycle))
        return self.heater_duty_cycle

    def get_heater_duty_cycle(self):
        return self.heater_duty_cycle

    def control_fan(self, throttle):
        self.fan_throttle = throttle
        print('fan throttle: {:.5f}'.format(throttle))
        return self.fan_throttle

    def get_fan_throttle(self):
        return self.fan_throttle

    def read_temperature(self):
        temperature = random.random() * 100.0
        print('thermocouple temperature: {:.5f}'.format(temperature))
        return temperature


def popper(testing):
    """
    Set up hardware and start event loop.
    """

    if testing:
        coffee_popper = TestPopper()
    else:
        import coffee_popper.rpi_popper as rpi
        coffee_popper = rpi.CoffeePopper()

    try:
        context = zmq.Context()
        control_socket = context.socket(zmq.REP)
        control_socket.bind("tcp://*:5555")

        poller = zmq.Poller()
        poller.register(control_socket, zmq.POLLIN)

        status_socket = context.socket(zmq.PUB)
        status_socket.bind("tcp://*:5556")

        message_handlers = {
            'heater': coffee_popper.control_heater,
            'fan': coffee_popper.control_fan,
            'read_temperature': coffee_popper.read_temperature
        }

        next_status_msg_time = time.time()
        while True:
            socks = dict(poller.poll(timeout=10))
            if control_socket in socks:
                # get a list of messages
                json_messages = control_socket.recv_json()
                print("Received request:\n{}".format(json_messages))

                for function_name, function_kwargs in json_messages:
                    print('\tfunction name: {}'.format(function_name))
                    print('\tfuncation args: {}'.format(function_kwargs))
                    #function_name = json_message[0]
                    #function_kwargs = json_message[1]
                    message_handler = message_handlers[function_name]
                    response = message_handler(**function_kwargs)

                    json_response = {
                        function_name: response
                    }

                    #  Send reply back to client
                    control_socket.send_json(json_response)

            else:
                pass

            # time for a status message?
            if time.time() >= next_status_msg_time:
                status = {
                    'status': {
                        'time': time.time(),
                        'temperature': coffee_popper.read_temperature(),
                        'fan_throttle': coffee_popper.get_fan_throttle(),
                        'heater_duty_cycle': coffee_popper.get_heater_duty_cycle()
                    }
                }
                print('sending a status message:\n{}'.format(status))
                status_msg = ("status {}".format(json.dumps(status)))
                print('status_msg: {}'.format(status_msg))
                status_socket.send_string(status_msg)
                # next status message 1s after the previous time
                next_status_msg_time += 1.0

            else:
                pass

    finally:
        print('Clean it up!')
        coffee_popper.cleanup()


if __name__ == '__main__':
    popper(testing=False)

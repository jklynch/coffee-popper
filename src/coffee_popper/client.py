import json
import time

import zmq


class PopperClient:
    def __init__(self, popper_ip_address):
        self.popper_ip_address = popper_ip_address
        self.context = zmq.Context()

        self.control_socket = self.context.socket(zmq.REQ)
        self.control_socket.connect("tcp://{}:5555".format(self.popper_ip_address))

        self.status_socket = self.context.socket(zmq.SUB)
        self.status_socket.connect("tcp://{}:5556".format(self.popper_ip_address))
        self.status_socket.setsockopt_string(zmq.SUBSCRIBE, "status ")

        self.poller = zmq.Poller()
        self.poller.register(self.status_socket, zmq.POLLIN)

        self.get_status()

    def get_status(self):
        # need to sleep
        time.sleep(1)
        socks = dict(self.poller.poll(timeout=10))
        if self.status_socket in socks:
            status_env = self.status_socket.recv_string()
            status_msg = status_env[6:]
            print('status message:\n{}'.format(status_msg))
            status = json.loads(status_msg)
            # t = status['status']['time']
            # temp_c = status['status']['temperature']
            return status['status']
        else:
            raise Exception('no popper status')

    def set_heater_duty_cycle(self, duty_cycle):
        message = [
            'heater', {'duty_cycle': duty_cycle}
        ]
        self.control_socket.send_json(message)
        json_msg = self.control_socket.recv_json()

    def set_fan_throttle(self, throttle):
        message = [
            'fan', {'throttle': throttle}
        ]
        self.control_socket.send_json(message)
        json_msg = self.control_socket.recv_json()

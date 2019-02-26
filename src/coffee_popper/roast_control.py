import json
import sys

import zmq


def roast_control(roaster_ip):
    try:
        context = zmq.Context()
        control_socket = context.socket(zmq.REQ)
        control_socket.connect("tcp://{}:5555".format(roaster_ip))

        sub_socket = context.socket(zmq.SUB)
        sub_socket.connect("tcp://{}:5556".format(roaster_ip))

        poller = zmq.Poller()
        poller.register(control_socket, zmq.POLLIN)
        poller.register(sub_socket, zmq.POLLIN)

        while True:

            msg = input()
            msg_elements = msg.split()
            print(msg_elements)
            function_name = msg_elements[0]
            messages = [
                (function_name, {})
            ]
            if len(msg_elements) > 1:
                arg_name = msg_elements[1]
                arg_value = float(msg_elements[2])
                message_args = messages[0][1]
                message_args[arg_name] = arg_value

            json_msg = json.dumps(messages)
            print(json_msg)
            control_socket.send_json(messages)

            json_msg = control_socket.recv_json()
            print(json_msg)

    finally:
        print('clean up?')


if __name__ == '__main__':
    roaster_ip = sys.argv[1]
    roast_control(roaster_ip)

import json
import sys

import matplotlib.pyplot as plt
import matplotlib.animation as animation

import zmq


def roast_plot(roaster_ip):
    context = zmq.Context()
    status_socket = context.socket(zmq.SUB)
    status_socket.connect("tcp://{}:5556".format(roaster_ip))
    status_socket.setsockopt_string(zmq.SUBSCRIBE, "status ")

    poller = zmq.Poller()
    poller.register(status_socket, zmq.POLLIN)

    # Create figure for plotting
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    xs = []
    ys = []

    # This function is called periodically from FuncAnimation
    def animate(i, xs, ys):
        ##print('animate {}'.format(i))
        socks = dict(poller.poll(timeout=10))
        if status_socket in socks:
            status_env = status_socket.recv_string()
            status_msg = status_env[6:]
            print('status message:\n{}'.format(status_msg))
            status = json.loads(status_msg)
            t = status['status']['time']
            temp_c = status['status']['temperature']

            # Add x and y to lists
            xs.append(t)
            ys.append(temp_c)

            # Limit x and y lists to 20 items
            xs = xs[-20:]
            ys = ys[-20:]

            # Draw x and y lists
            ax.clear()
            ax.plot(xs, ys)

            # Format plot
            plt.ylim(0.0, 400.0)
            plt.xticks(rotation=45, ha='right')
            plt.subplots_adjust(bottom=0.30)
            plt.title('Coffee Popper Temperature')
            plt.ylabel('Temperature (deg C)')

    # Set up plot to call animate() function periodically
    ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys))
    plt.show()


if __name__ == '__main__':
    _roaster_ip = sys.argv[1]
    roast_plot(_roaster_ip)

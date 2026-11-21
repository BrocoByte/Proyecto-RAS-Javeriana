import sys
import termios
import tty
import rclpy
from std_msgs.msg import String

KEYS = {'w': 'forward', 's': 'backward', 'a': 'left', 'd': 'right', ' ': 'stop'}
HELP = "w: adelante | s: atras | a: izquierda | d: derecha | espacio: stop | q: salir"


def get_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def main():
    rclpy.init()
    node = rclpy.create_node('teleop_keyboard')
    pub = node.create_publisher(String, 'robot_cmd', 10)
    print(HELP)
    try:
        while True:
            k = get_key().lower()
            if k == 'q' or k == '\x03':
                break
            if k in KEYS:
                pub.publish(String(data=KEYS[k]))
                print(f'-> {KEYS[k]}\r')
    finally:
        pub.publish(String(data='stop'))
        node.destroy_node()
        rclpy.shutdown()

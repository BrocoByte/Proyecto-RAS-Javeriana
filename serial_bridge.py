import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Float32
import serial

VALID = {'forward', 'backward', 'left', 'right', 'stop'}


class SerialBridge(Node):
    """/robot_cmd (String) -> serial -> ESP32. ESP32 -> /distance_cm y /obstacle."""

    def __init__(self):
        super().__init__('serial_bridge')
        self.declare_parameter('host', '/dev/ttyACM0')
        self.declare_parameter('baud_rate', 115200)
        host = self.get_parameter('host').value
        baud_rate = self.get_parameter('baud_rate').value

        self.ser = serial.Serial(host, baud_rate, timeout=0.1)
        self.sub = self.create_subscription(String, 'robot_cmd', self.on_cmd, 10)
        self.pub_dist = self.create_publisher(Float32, 'distance_cm', 10)
        self.pub_obs = self.create_publisher(String, 'obstacle', 10)
        self.create_timer(0.02, self.read_serial)
        self.get_logger().info(f'Conectado a {host} @ {baud_rate}')

    def on_cmd(self, msg):
        cmd = msg.data.strip().lower()
        if cmd not in VALID:
            self.get_logger().warn(f'Comando invalido: {cmd}')
            return
        self.ser.write((cmd + '\n').encode())

    def read_serial(self):
        while self.ser.in_waiting:
            line = self.ser.readline().decode(errors='ignore').strip()
            if line.startswith('D:'):
                try:
                    self.pub_dist.publish(Float32(data=float(line[2:])))
                except ValueError:
                    pass
            elif line == 'OBSTACLE':
                self.pub_obs.publish(String(data='obstacle'))
                self.get_logger().warn('Obstaculo: robot detenido')

    def destroy_node(self):
        try:
            self.ser.write(b'stop\n')
            self.ser.close()
        except Exception:
            pass
        super().destroy_node()


def main():
    rclpy.init()
    node = SerialBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2 as cv


from time import time


class Process(Node):
    def __init__(self):
        super().__init__('process')
        self.jst4dof_sub = self.create_subscription(
            String,
            'jst4dof_values',
            self.jst4dof_values_parser,
            1)
        self.glasses_sub = self.create_subscription(
            Image,
            'glasses_source',
            self.glasses_source_parser,
            1)
        
        self.odriver_pub = self.create_publisher(String, 'odriver_input', 1)
        self.timer = self.create_timer(0.01, self.publish_odriver_input)

        self.odriver_pkg = 'brake 0 0'
        self.jst4dof_pkg = {'button': 0, 'rotate': 0, 'joystX': 0, 'joystY': 0}

        self.cmd: bool    = 'brake'
        self.val_l: float = 0
        self.val_r: float = 0

        self.mode: bool = False
        self.mode_tmr = time()

        self.vel_lim = 4

        self.bridge = CvBridge()
        
    def jst4dof_values_parser(self, msg):
        unpacked_msg = list(map(int, msg.data.split()))

        self.jst4dof_pkg['button'] = unpacked_msg[0]
        self.jst4dof_pkg['rotate'] = unpacked_msg[1]
        self.jst4dof_pkg['joystX'] = unpacked_msg[2]
        self.jst4dof_pkg['joystY'] = unpacked_msg[3]

        if self.jst4dof_pkg['button'] and self.mode_tmr + 0.5 < time():
            self.mode = not self.mode
            self.mode_tmr = time()
        
        if not self.mode:
            self.val_l = 0
            self.val_r = 0
            self.cmd = 'stop' # free movement
            return 

        # all in zero
        if not self.jst4dof_pkg['rotate'] and \
           not self.jst4dof_pkg['joystX'] and \
           not self.jst4dof_pkg['joystY']:
            self.val_l = 0
            self.val_r = 0
            self.cmd = 'brake' # motor can not move free
            return 
        
        rotate   = self.map(self.jst4dof_pkg['rotate'], -100, 100, -self.vel_lim, self.vel_lim) * 0.5
        throttle = self.map(self.jst4dof_pkg['joystY'], -100, 100, -self.vel_lim, self.vel_lim) 
        turn     = self.map(self.jst4dof_pkg['joystX'], -100, 100, -self.vel_lim, self.vel_lim) * 0.5

        self.cmd = 'set_vel'
        if throttle < 0: turn *= -1
        self.val_l = round(self.clamp_vel(throttle + turn + rotate), 2)
        self.val_r = round(self.clamp_vel(throttle - turn - rotate), 2)

    def glasses_source_parser(self, src):
        frame = self.bridge.imgmsg_to_cv2(src)

        cv.imshow('frame', frame)
        cv.waitKey(1)

    def publish_odriver_input(self):
        msg = String()
        msg.data = f'{self.cmd} {self.val_l} {self.val_r}'
        self.odriver_pub.publish(msg)

    @staticmethod
    def map(x, in_min, in_max, out_min, out_max) -> float:
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

    def clamp_vel(self, vel) -> float:
        if vel > self.vel_lim:
            return self.vel_lim
        elif vel < -self.vel_lim:
            return -self.vel_lim
        else:
            return vel

        
def main(args=None):
    rclpy.init(args=args)

    process = Process()
    rclpy.spin(process)
    
    process.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
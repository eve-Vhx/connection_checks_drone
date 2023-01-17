#!/usr/bin/env python3

from __future__ import print_function
import threading 
from msg_pkg.msg import connections_drone
from mavros_msgs.msg import State
import rosnode
import rospy
import urllib


class ConnectionChecks:

    def __init__(self):
        rospy.init_node('connection_checks_drone')
        server_pub = rospy.Publisher("d1_connection_checks", connections_drone, queue_size=10)
        px4_sub = rospy.Subscriber("/mavros/state", State, self.px4_cb)
        self.rate = rospy.Rate(2)

        self.mavros_state = False
        self.px4_state = False
        self.wifi_state = False
        self.lte_state = False

        self.timer = threading.Timer(5,self.timeout)
        self.timer.start()

        self.run_checks()

    def timeout(self):
        print("PX4 OFF")
        self.px4_state = False

    def px4_cb(self):
        print("PX4 ON")
        self.timer.cancel()
        self.timer = threading.Timer(5,self.timeout)
        self.timer.start()
        self.mavros_state = True

    def run_checks(self):
        while not rospy.is_shutdown():
            active_nodes = rosnode.get_node_names()
            for node in active_nodes:
                if(node == '/mavros'):
                    print("Mavros ON")
                    mavros_state = True
                else:
                    print("Mavros OFF")
                    mavros_state = False
                    px4_state = False

            try:
                url = "https://www.google.com"
                urllib.urlopen(url)
                self.wifi = True
                self.lte = True
            except:
                self.wifi = False
                self.lte = False

        checks_msg = connections_drone()
        checks_msg.wifi = self.wifi_state
        checks_msg.lte = self.lte_state
        checks_msg.mavros = self.mavros_state
        checks_msg.px4 = self.px4_state

        self.server_pub.Publish(checks_msg)
        self.rate.sleep()


        

if __name__ == "__main__":
    ConnectionChecks()
    rospy.spin()
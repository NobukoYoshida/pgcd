# ROSL - Concurrent Control Code in ROS with resources and frames tracking

ROSL is a programming language for ROS nodes.

## Features

Currently the main functionalities of ROSL are:
* Communication between ROS nodes (ROS message & ROS topics)
* Execute motion primitive (CableRobot project by Marcus Pirron)
* Tracking frames (TF2 library)

## Project setup (tried on Ubuntu16.04 LTS and Debian GNU/Linux 8 (jessie))

To run ROSL you need to:

* install ROS ( reccomended ROS Kinetic: http://wiki.ros.org/kinetic/Installation)
* install tf2 library with turtlesim 

```
sudo apt-get install ros-$ROS_DISTRO-turtle-tf2 ros-$ROS_DISTRO-tf2-tools ros-$ROS_DISTRO-tf
```

* create a catkin workspace having in mind python3 (compile geometry package with python3):

```
$ mkdir catkin_ws
$ cd catkin_ws
$ mkdir src
$ cd src 
$ git clone https://github.com/ros/geometry
$ git clone https://github.com/ros/geometry2
$ cd ..
$ virtualenv -p /usr/bin/python3 venv
$ source venv/bin/activate
$ pip install catkin_pkg pyyaml empy rospkg numpy ply sympy enum34 arpeggio defusedxml
```

* make sure you have installed bullet library:

```
$ sudo apt-get install libbullet-dev
```

or follow: https://answers.ros.org/question/220676/how-to-install-bullet-on-indigo-in-ubuntu/

* also make sure you installed python header files:
 
```
$ sudo apt-get install python3-dev
```

* download this project in your catkin workspace

```
$ cd ~/Dowloads
$ git clone https://gitlab.mpi-sws.org/gbbanusic/chor-and-frames-for-conc-ctrl-code.git rfccc
$ cp -a rfccc/. ~/catkin_ws/src/
```

* compile and source:

```
$ cd ~/catkin_ws
$ catkin_make --force-cmake
$ echo "source ~/catkin_ws/devel/setup.bash" >> ~/.bashrc
```

For more details how to compile tf2 with python3 see: https://github.com/ros/geometry2/issues/259 .
If you want your computer to store permanently your workspace you need to add the
listed command into your .bashrc file in "home/user/" directory.

## RUN Example

### With PyCharm IDE

If you have PyCharm you can open the rfccc directory as project:
* set rfccc/nodes and rfccc/nodes/interpreter files as source roots (right click on them -> mark directory as -> source root)
* go to Settings -> Project: rfccc -> Project interpreter -> add python3 venv ([Picture](https://gitlab.mpi-sws.org/gbbanusic/chor-and-frames-for-conc-ctrl-code/blob/master/readme/set_venv.png))
* import CableRobot project or modify the project to remove dependencies (will be done in future)


To run the example you need to:

* Run main.py file


* Run terminal command for starting roscore

```
$ roslaunch rfccc start.launch
```

* Run terminal command for visualisation

```
$ rosrun rviz rviz -d `rospack find turtle_tf2`/rviz/turtle_rviz.rviz
```

from setuptools import setup

package_name = 'robot_ras'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools', 'pyserial'],
    zip_safe=True,
    entry_points={
        'console_scripts': [
            'serial_bridge = robot_ras.serial_bridge:main',
            'teleop_keyboard = robot_ras.teleop_keyboard:main',
        ],
    },
)

from setuptools import find_packages, setup

package_name = 'vision_ride'
submodules = 'vision_ride/submodules'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='vanische',
    maintainer_email='vanischesmall@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'jst4dof = vision_ride.jst4dof:main',
            'process = vision_ride.process:main',
            'odriver = vision_ride.odriver:main',
            'glasses = vision_ride.glasses:main',
        ],
    },
)

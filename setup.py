from setuptools import setup

setup(name='mqtt-lightify',
      version='0.1',
      description='Connects between MQTT and a lightify bridge.',
      url='https://github.com/dzerrenner/mqtt-lightify',
      author='David Zerrenner',
      author_email='dazer017@gmail.com',
      license='MIT',
      packages=['mqtt-lightify'],
      setup_requires=["pytest-runner", "lightify", "paho-mqtt"],
      tests_require=["pytest", "lightify", "paho-mqtt"],
      zip_safe=False)
# Publish a state change message for HomeMatic devices
# Parameters:
#   -h Hostname of the mqtt broker
#   -t Message topic. This is in the format for the mqtt node which is builtin to RedMatic:
#       hm/<verb>/<device>/<dataPoint>
#   -m The message itself, for switching devices, the value is either 0/1 or true/false

# switch
mosquitto_pub -h 192.168.178.30 -t hm/set/000218A995F0CB:3/STATE -m "true"

# set temperature
mosquitto_pub -h 192.168.178.30 -t hm/set/000393C99BB735:1/SET_POINT_TEMPERATURE -m "20.0"
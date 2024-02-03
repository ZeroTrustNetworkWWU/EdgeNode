from enum import Enum

# Enum for all special requests that can be sent to the edge node
class RequestType(Enum):
    GENERIC = 0
    LOGIN = 1
    LOGOUT = 2
    REGISTER = 3
    REMOVE_ACCOUNT = 4
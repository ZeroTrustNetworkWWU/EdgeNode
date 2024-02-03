class MissingTrustData(Exception):
    def __init__(self, message):
        super().__init__(message)

class LowClientTrust(Exception):
    def __init__(self, message):
        super().__init__(message)

class MyClass:
    """Test class that does nothing"""

    test = 59646
    
    def __init__(self, value=1):
        self.test = value

    def get(self):
        return self.test

    def hello(self):
        print("Hi there! This sis some greeting")

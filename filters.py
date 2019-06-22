#!/usr/bin/env python3

class HighPass():
    def __init__(self,a):
        self.a = a
        self.last_x = None
        self.y = 0.0

    def __call__(self,x):

        if self.last_x is None:
            self.last_x = x
            return 0.0

        self.y = self.a * (self.y + x - self.last_x)
        self.last_x = x
        return self.y
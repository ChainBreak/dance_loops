#!/usr/bin/env python3

class HighPass():
    def __init__(self,a):
        self.a = a
        self.last_x = None
        self.y = 0.0

    def __call__(self,x):
        self.y = self.a * (self.y + x - self.last_x)
        return self.y
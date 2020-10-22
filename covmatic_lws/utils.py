from functools import wraps, partial
from threading import Timer


class SingletonMeta(type):
    def __new__(meta, name, bases, classdict):
        def new(cls, *args, **kwargs):
            if cls._inst is None:
                if super(cls, cls).__new__ is object.__new__:
                    args = []
                    kwargs = {}
                cls._inst = super(cls, cls).__new__(cls, *args, **kwargs)
            return cls._inst
        
        classdict["__new__"] = classdict.get("__new__", new)
        return super(SingletonMeta, meta).__new__(meta, name, bases, classdict)
    
    def __init__(cls, name, bases, classdict):
        super(SingletonMeta, cls).__init__(name, bases, classdict)
        cls._inst = None
    
    def reset(cls, *args, **kwargs):
        del cls._inst
        cls._inst = None
        if args or kwargs:
            cls._inst = cls(*args, **kwargs)
        return cls._inst


class ClassProperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, inst, cls=None):
        return self.fget.__get__(inst, cls or type(inst))()


def classproperty(foo):
    return ClassProperty(foo if isinstance(foo, (classmethod, staticmethod)) else classmethod(foo))


def locked(lock):
    def _locked(foo):
        @wraps(foo)
        def _foo(*args, **kwargs):
            with lock:
                r = foo(*args, **kwargs)
            return r
        return _foo
    return _locked


class LoopFunction:
    def __init__(self, interval, func):
        self._interval = interval
        self._func = func
        self._thread = None
    
    def stop(self):
        if self._thread is not None:
            self._thread.cancel()
    
    def start_(self):
        self._func()
        self.start()
    
    def start(self):
        self._thread = Timer(self._interval, self.start_)
        self._thread.start()


def loop(interval):
    def _looped(foo):
        return LoopFunction(interval, foo)
    return _looped


class FunctionCase(dict):
    def __init__(self, key):
        super(FunctionCase, self).__init__()
        self._key = key
    
    def case(self, key, value=None):
        if value is None:
            return partial(self.case, key)
        for k in key if isinstance(key, tuple) else (key,):
            self[k] = value
        return value
        
    def __call__(self, *args, **kwargs):
        if self._key not in self:
            raise NotImplementedError("No function implemented for case '{}'. Supported cases are: {}".format(self._key, ", ".join(map("'{}'".format, self.keys()))))
        return self[self._key](*args, **kwargs)


# Copyright (c) 2020 Covmatic.
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import collections.abc
import string
import struct
import sys

class FixedHash(collections.abc.MutableMapping):
    hashsize = 8
    def __init__(self, elementsize, size):
        self.elementsize = elementsize
        self.size = size
        self.entrysize = self.hashsize + self.elementsize * 2
        self.format = 'q{}s{}s'.format(self.elementsize, self.elementsize)
        assert struct.calcsize(self.format) == self.entrysize
        self.zero = b'\0' * self.elementsize
        self.store = bytearray(struct.pack(self.format, 0,
                                           self.zero, self.zero)
                               ) * self.size
        self.len = 0
        self._probecount = 0
    def _hash(self, k):
        return hash(k) or 1
    def _stash(self, i, h, k, v):
        entry = struct.pack(self.format, h, k, v)
        self.store[i*self.entrysize:(i+1)*self.entrysize] = entry
    def _fetch(self, i):
        entry = self.store[i*self.entrysize:(i+1)*self.entrysize]
        return struct.unpack(self.format, entry)
    def _probe(self, keyhash):
        i = keyhash % self.size
        while True:
            h, k, v = self._fetch(i)
            yield i, h, k, v
            i = (i + 1) % self.size
            if i == keyhash % self.size:
                break
            self._probecount += 1
    def __getitem__(self, key):
        keyhash = self._hash(key)
        for i, h, k, v in self._probe(keyhash):
            if h and k == key:
                return v
        assert False, 'WTF?!'
    def __delitem__(self, key):
        keyhash = self._hash(key)
        for i, h, k, v in self._probe(keyhash):
            if h and k == key:
                self._stash(i, 0, self.zero, self.zero)
                self.len -= 1
                return
        raise KeyError(key)
    def __setitem__(self, key, value):
        keyhash = self._hash(key)
        for i, h, k, v in self._probe(keyhash):
            if not h or k == key:
                if not h:
                    self.len += 1
                self._stash(i, keyhash, key, value)
                return
        raise ValueError('hash table full')
    def __iter__(self):
        for i in range(self.size):
            h, k, v = self._fetch(i)
            if h:
                yield k
    def __len__(self):
        return self.len
    def __repr__(self):
        return '{}({})'.format(type(self).__name__, dict(self.items()))

def test(size=32, count=32, usedict=False):
    import random
    d = {} if usedict else FixedHash(4, size)
    letters = string.ascii_lowercase.encode('ascii')
    def make():
        return bytes(random.choice(letters) for _ in range(4))
    for i in range(count):
        k = make()
        d[k] = make()
        d[k] = make()
    try:
        d[make()] = make()
    except ValueError as e:
        # expected if you're inserting 33 values into a 32-max hash
        pass 
    for i in range(count//2):
        d.popitem()
    try:
        return d._probecount
    except:
        return 0

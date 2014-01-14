fixedhash
=========

A hashtable for compact storage of fixed-size values (fixedhash:dict :: array:list)

This is not meant to be used for serious code, only as a demonstration of the idea.

API
---

A `fixedhash` provides the full `MutableMapping` API, like a `dict`.

However, like a `dbm`, its keys and values must be bytes (or bytes-compatible types). You can of course "decorate" other objects to store them, but you have to do that manually.

Unlike a `dbm`, its keys and values must also be fixed size, specified at construction time. This is critical to the design.

In fact, keys and values have to be the same size as each other; there's no good reason for that short of saving one line of code.

There may not be sufficient error handling; there could easily be ways to corrupt the table by, e.g., storing a 6-byte value when the object is expecting 8 bytes.

The hashtable itself has fixed capacity, specified at construction time; this is not critical to the design, it was just done to make the implementation simpler. If you try to insert more values than its capacity, you will get a `ValueError`.

In addition to the standard `dict` members, a `fixedhash` also provides a variety of other members. The most interesting are probably `size` (capacity), `elementsize`, `store` (the underlying data store), and `_probecount` (explained below).

Space
-----

The hashes, keys, and values are all stored together in a single `bytearray`, which avoids the overhead of holding three "boxed" Python objects (each typically with 24-48 bytes of overhead) per key-value pair. If you're mapping small keys to small values, this can easily cut your storage by 75%.

If your Python uses 32-bit hashes, you probably want to change `FixedDict.hashsize` to 4.

Time
----

Remember, this is sample code, not a production-ready library.

The hash uses (the stupidest possible) linear chaining for collisions. Because it's fixed, it cannot provide an O(1) amortized time guarantees; the more you load the table, the slower it will get. For profiling purposes, the load is `len(d) / d.size`, and `d._probecount` tells you how may probes have been needed (a measure of how much time you wasting by having load too high).

Various other standard optimizations (e.g., requiring size to be 2^N-1 so you can bitmask the hash instead of modding) are left out. In fact, an extra pessimization was added, colliding hash 0 with hash 1 to save space for a "free" marker (which may not be a terrible idea, but using 0 might be…).

The implementation also leans on `collections.abc.MutableMapping` as much as possible; some methods could be significantly faster than the generic version.

It's possible that for some applications, just reimplementing this in Cython or running in PyPy instead of CPython, and tuning the size correctly, and maybe picking a better probing algorithm, would make this faster than a `dict` (thanks to cache locality). But for untuned general-purpose use, expect it to be slow as hell.

From some quick tests with 32-byte keys and values, a fixedhash is always at least 3x slower than a dict, and up to 278x slower.

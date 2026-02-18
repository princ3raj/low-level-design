import weakref
import gc

class Listener:
    def __repr__(self):
        return "TempListener"

# 1. Strong Reference (List)
strong_list = []
l1 = Listener()
strong_list.append(l1)

print(f"List holds: {strong_list}")
del l1 # I am done with l1
gc.collect()
print(f"List AFTER delete: {strong_list} <-- LEAK! Object still alive because list holds it.")

print("-" * 20)

# 2. Weak Reference (WeakSet)
weak_set = weakref.WeakSet()
l2 = Listener()
weak_set.add(l2)

print(f"WeakSet holds: {list(weak_set)}")
del l2 # I am done with l2
gc.collect()
print(f"WeakSet AFTER delete: {list(weak_set)} <-- GONE! Object destroyed automatically.")

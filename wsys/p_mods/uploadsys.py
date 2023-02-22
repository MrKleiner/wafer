# todo: It's super easy to log all the incoming socket connections and put these logs into a database
# (a threshold indicating the maximum amount of logs kept is the easiest way of solving memory issues)
# (todo: also log unsuccessful login attempts to prove idiots that they're imbeciles ?)
# since each multiprocessing.Process returns an object indicating whether the process was finished or not - 
# a tuple of (process_obj, start time, IP, PID, whatever ..)
# can be appended to an array within acceptable context regularly checked by a thread within the same context.
# (aka access is not direct, but being read from the disk where it was saved by autonomous function)
# important todo: reliably deleting obsolete Process references. Is deleting them from the array enough?

# important todo: https://stackoverflow.com/questions/16090530/how-to-point-a-websocket-to-the-current-server
# todo: https://docs.python.org/3/library/os.html
# todo: https://docs.python.org/3/library/sys.html
# todo: https://docs.python.org/3/library/multiprocessing.html
# todo: https://docs.python.org/3/library/socket.html
# todo: https://docs.python.org/3/library/multiprocessing.shared_memory.html
# todo: https://superfastpython.com/multiprocessing-share-object-with-processes/
# todo: https://stackoverflow.com/questions/26499548/accessing-an-attribute-of-a-multiprocessing-proxy-of-a-class

# Yes, the file upload module does not allow super versatile status retrieval, but it's not needed:
# Simply create a copy of the queue for each room and delete it asap if it's not needed
# BUT this is actually a very bad idea
# This is very sad since it's literally the only way of having any feedback from this process...
# This is giga sad, since the dream of "terminate this fucker's connection" may never come true...
# EXCEPT, it's possible to get processes' PID and kill it by PID !



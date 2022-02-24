import queue


class MessageAnnouncer:
    def __init__(self):
        self.listeners = []

    def listen(self):
        self.listeners.append(queue.Queue(maxsize=10))
        return self.listeners[-1]

    def announce(self, msg):
        for i in reversed(range(len(self.listeners))):
            try:
                self.listeners[i].put_nowait(msg)
            except queue.Full:
                del self.listeners[i]


METRICS_ANNOUNCER = MessageAnnouncer()
EVENTS_ANNOUNCER = MessageAnnouncer()

import asyncio
from typing import Callable, Any, Dict, List, Union

class EventQueue:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EventQueue, cls).__new__(cls)
            cls._instance.queue = asyncio.Queue()
        return cls._instance

    async def put(self, item):
        await self.queue.put(item)

    async def get(self):
        return await self.queue.get()

    def task_done(self):
        self.queue.task_done()

class Event:
    def __init__(self, tag: str):
        self.tag = tag
        self.handlers: List[Callable] = []

    def connect(self, handler: Callable):
        self.handlers.append(handler)

    async def trigger(self, data: Any = None):
        await EventQueue().put((self, data))

class EventBasedObject:
    def __init__(self):
        self.events: Dict[str, Event] = {}

    def create_event(self, tag: str) -> Event:
        event = Event(tag)
        self.events[tag] = event
        return event

class EventBasedApp:
    def __init__(self):
        self.event_queue = EventQueue()

    async def run(self):
        while True:
            event, data = await self.event_queue.get()
            for handler in event.handlers:
                if asyncio.iscoroutinefunction(handler):
                    await handler(data)
                else:
                    handler(data)
            self.event_queue.task_done()

    async def start(self):
        await self.run()

# Example usage
class MyClass(EventBasedObject):
    def __init__(self):
        super().__init__()
        self.event1 = self.create_event("event1")
        self.event2 = self.create_event("event2")

async def main():
    app = EventBasedApp()
    my_object = MyClass()

    # Define handlers
    async def async_handler1(data):
        print(f"Async Handler 1 received: {data}")
        await my_object.event2.trigger("Data from event1")

    def sync_handler1(data):
        print(f"Sync Handler 1 received: {data}")

    async def async_handler2(data):
        print(f"Async Handler 2 received: {data}")

    # Connect handlers to events
    my_object.event1.connect(async_handler1)
    my_object.event1.connect(sync_handler1)
    my_object.event2.connect(async_handler2)

    # Trigger events
    await my_object.event1.trigger("Hello from main")

    # Run the application
    await app.start()

if __name__ == "__main__":
    asyncio.run(main())
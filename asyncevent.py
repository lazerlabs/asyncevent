import asyncio
import inspect
import typing as t
from dataclasses import dataclass

@dataclass
class BaseEventData:
    ...

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
    def __init__(self, event_name: str):
        caller_frame = inspect.currentframe().f_back
        caller_class = caller_frame.f_locals.get('self', None).__class__.__name__
        self.event_name = event_name.upper()
        self._internal_event_name: str = f"{caller_class}.{event_name.upper()}"
        self.handlers: t.List[t.Callable] = []

    async def trigger(self, event_data: t.Union[BaseEventData, None] = None):
        await EventQueue().put(self, event_data)

    def register_handler(self, handler: t.Callable[[t.Union[BaseEventData,None]], None]):
        self.event_manager.register_handler(self._internal_event_name, handler)

    def __str__(self) -> str:
        return self.event_name

    def __repr__(self):
        return f"<Event {self.event_name}>"

class EventBasedObject:
    def __init__(self):
        self.events: t.Dict[str, Event] = {}

    def create_event(self, event_name: str) -> Event:
        event = Event(event_name)
        self.events[event_name] = event
        return event
    
    def __getattr__(self, name: str) -> Event:
        if name in self.events:
            return self.events[name]
        return super().__getattr__(name)
    
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


def eventful_class(cls):
    if hasattr(cls, '_events'):
        cls.events = [Event(event_name) for event_name in cls._events]
    return cls

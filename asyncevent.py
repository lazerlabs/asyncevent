import asyncio
import inspect
from typing import Callable, Dict, Set
from dataclasses import dataclass

@dataclass
class BaseEventData:
    ...

class EventApp:
    def __init__(self):
        self.event_manager = EventManager()

    async def run(self):
        task = asyncio.create_task(self.event_manager.run())
        await self.main()
        await task    

    async def main(self):
        raise NotImplementedError("main method not implemented")


class EventManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self._events: Dict[str, Set[Callable]] = {}
        self._event_queue: asyncio.Queue = asyncio.Queue()

    def register_handler(self, event_name: str, handler: Callable):
        if event_name not in self._events:
            self._events[event_name] = set()
        self._events[event_name].add(handler)
        print(f"Registered handler {handler} for event {event_name}")

    async def trigger_event(self, event_name: str, event_data: BaseEventData):
        handlers = self._events.get(event_name)
        print(f"Triggering event {event_name} with data {event_data}")
        if handlers:
            for handler in handlers:
                print(f"Triggering handler {handler}")
                await self._event_queue.put((handler, event_data))
        else:
            raise ValueError(f"No handler registered for event {event_name}")
        
    async def run(self):
        while True:
            handler, event_data = await self._event_queue.get()
            await handler(event_data)
        

class Event:
    def __init__(self, event_name: str):
        caller_frame = inspect.currentframe().f_back
        caller_class = caller_frame.f_locals.get('self', None).__class__.__name__
        self.event_name = event_name.upper()
        self._internal_event_name: str = f"{caller_class}.{event_name.upper()}"
        self.event_manager: EventManager = EventManager()

    async def trigger(self, event_data: BaseEventData):
        await self.event_manager.trigger_event(self._internal_event_name, event_data)

    def register_handler(self, handler: Callable):
        self.event_manager.register_handler(self._internal_event_name, handler)

    def __str__(self) -> str:
        return self.event_name

    def __repr__(self):
        return f"<Event {self.event_name}>"

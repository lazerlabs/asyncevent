from asyncevent import EventApp, Event, BaseEventData
import asyncio
from dataclasses import dataclass

@dataclass
class NumberGeneratorEventData(BaseEventData):
    number: int

class NumberGenerator:
    _events = [
        "NUMBER_GENERATED"
    ]

    def __init__(self, start: int= 0, end: int = 1_000_000):
        self.start = start
        self.end = end
        self.number = self.start
        self.events = {}
        for event_name in self._events:
            self.events[event_name] = Event(event_name)
    
    async def generate(self):
        while self.number < self.end:
            self.number += 1
            await self.events["NUMBER_GENERATED"].trigger(NumberGeneratorEventData(number=self.number))
            await asyncio.sleep(1)
 


class TestApp(EventApp):

    def __init__(self):
        super().__init__()
        self.events = {
            "FIZZ": Event("FIZZ"),
            "BUZZ": Event("BUZZ"),
        }
  
    async def fizzbuzz(self, event_data: NumberGeneratorEventData):
        if event_data.number % 3 == 0:
            await self.events["FIZZ"].trigger(event_data)
        elif event_data.number % 5 == 0:
            await self.events["BUZZ"].trigger(event_data)
        else:
            print(event_data.number)

    async def fizz(self, event_data: NumberGeneratorEventData):
        print("Fizz")

    async def buzz(self, event_data: NumberGeneratorEventData):
        print("Buzz")   

    async def main(self):
        self.events["FIZZ"].register_handler(self.fizz)
        self.events["BUZZ"].register_handler(self.buzz)


        number_generator = NumberGenerator()
        number_generator.events["NUMBER_GENERATED"].register_handler(self.fizzbuzz)
        number_generator_task = asyncio.create_task(number_generator.generate())
        await number_generator_task

if __name__ == "__main__":
    test_app = TestApp()
    asyncio.run(test_app.run())

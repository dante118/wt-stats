# from WTwebdev import telemetry, mapinfo
from WTwebdev.mapinfo import MapInfo
from WTwebdev.telemetry import TelemInterface
from WTwebdev.telemetry import Status
import re
from time import sleep

from enum import StrEnum




class WTstats():

    def __init__(self):
        self.stats = {}
        self.critical = []
        self.fatal = []
        self.status = Status.WT_NOT_RUNNING
        self.UPTIME = 1
        self.tm = TelemInterface()
        self.mp = MapInfo()

        self.player = 'mortumwish'
        self.plane = ''
    
    class Events(StrEnum):
        kill = 'сбил'
        critical = 'нанёс критическое повреждение'
        crash = 'разбился'
        fatal = 'нанёс фатальное повреждение'
    
    def update_stat(self, plane: str, type: str, value: int = 1) -> None:
        if plane not in self.stats:      
            self.stats.update({
                plane: {
                    'kills' : 0,
                    'deaths': 0,
                    'battles': 0,
                    'AIs': 0,
                    'assists':0
                }})
        try:
            self.stats[plane][type] += value
        except (KeyError, AttributeError):
            print('ERROR: failed to update statistics')

    def parse_event(self, event: list) -> None:
        event = [s.strip() for s in event]


        if len(event) > 2:
            try:
                if self.player in event[0]:
                    if self.Events.kill in event[2]:
                        self.update_stat(self.plane, 'kills')

                    elif self.Events.fatal in event[2]:
                        self.fatal.append(event[2].replace(self.Events.fatal.value, '').strip())

                    elif self.Events.critical in event[2]:
                        self.critical.append(event[2].replace(self.Events.critical.value, '').strip())

                    elif self.Events.crash in event[2]:
                        self.update_stat(self.plane, 'deaths')

                elif self.player in event[2] and self.Events.kill in event[2]:
                    self.update_stat(self.plane, 'deaths')
                    
                elif any(trg in event[2] for trg in self.fatal) and self.Events.kill in event[2]:
                    self.update_stat(self.plane, 'kills')
                        



            except Exception as e:
                print(e)
    
    def run(self) -> None:
        '''
        Starts main programm loop
        '''

        self.tm.get_events()
        self.tm.events.clear()


        try:


            while(True):
                new_status = self.tm.get_status()

                if self.status == new_status:
                    pass
                elif self.status == Status.IN_MENU:
                    if not self.mp.check_battle(True):
                        continue
                elif (self.status == Status.NO_MISSION) or (self.status == Status.WT_NOT_RUNNING) and (new_status == Status.IN_FLIGHT):
                    if not self.mp.check_battle(True):
                        new_status = Status.IN_MENU
                
                
                if self.status != new_status:

                    if new_status == Status.IN_FLIGHT:
                        self.plane = self.tm.basic_telemetry['airframe']
                        self.update_stat(self.plane, 'battles')



                    if new_status == Status.IN_MENU:
                        self.critical.clear()
                        self.fatal.clear()
                        if self.stats:
                            print('Вывести статистику')
                            print(self.stats)

                    
                    self.status = new_status
                    print('Changed to {}'.format(self.status))

                if self.status == Status.IN_FLIGHT:
                    self.plane = self.tm.basic_telemetry['airframe']
                    if self.tm.events:
                        for msg in self.tm.events:
                            event = re.findall(r"[^()]+", msg['msg']) # [src, src_veh, act+trg, trg_veh]
                            self.parse_event(event)
                        self.tm.events.clear()
            


                sleep(self.UPTIME)
        
        except KeyboardInterrupt:
            exit()
        


if __name__ == '__main__':
    
    app = WTstats()
    app.run()






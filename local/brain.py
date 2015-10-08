# -*- coding: utf-8 -*-

import logging
from engine.base import BaseBot
from engine.game_types import CraftItem

logger = logging.getLogger(__name__)


class LocalBrainBot(BaseBot):

    def perform_action(self):

        if not self.get_params().switch_local_brain_bot:
            return

        # Чистим закончившиеся платные мозги
        for buyed_brain in self.get_game_state().get_state().buyedBrains:
            if self.get_timer().has_elapsed(buyed_brain.endTime):
                self.get_game_state().get_state().buyedBrains.remove(buyed_brain)

        # Если нужно поддерживать мозги
        if self.get_params().buyed_brains_count:

            buyed_brains_count = self.get_params().buyed_brains_count
            activated_brains = 0

            for buyed_brain in self.get_game_state().get_state().buyedBrains:
                if not self.get_timer().has_elapsed(buyed_brain.endTime, -10):
                    activated_brains += buyed_brain.count

            delta_brains = buyed_brains_count - activated_brains
            if delta_brains:
                # список что мы будем крафтить вообще
                will_crafts = self.get_params().crafts
                found = False
                signal = u'brains',

                # Ищем нужную запись для крафтинга
                for will_craft in will_crafts:
                    if will_craft.signal == signal:
                        # Ставим нужное количество для крафтинга
                        will_craft.count = delta_brains

                        # отмечаем что нашли такую позицию
                        found = True

                        # активируем сигнал для крафта
                        self.get_game_state().set_signal(signal, True)
                        break

                # Если не нашли
                if not found:
                    # создаем сигнал для активации
                    self.get_game_state().set_signal(signal, True)

                    # создаем новый параметр для крафтинга с нужным нам значением
                    will_crafts.append(CraftItem(building=u'@B_OSTANKINO', craft_id=0, count=delta_brains,
                                                 signal=signal))

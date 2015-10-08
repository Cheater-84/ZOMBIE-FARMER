# -*- coding: utf-8 -*-

import logging
from engine.base import BaseBot
from engine.game_event import dict2obj
from engine.game_types import GameBuyItem, GameSellGameObject

logger = logging.getLogger(__name__)


class LocalPlaceBot(BaseBot):

    def __init__(self, game):
        super(LocalPlaceBot, self).__init__(game)

    def perform_action(self):

        if not self.get_params().switch_local_place_bot:
            return

        current_loc = self.get_game_state().get_game_loc().id

        if self.get_params().place_items_dict.get(current_loc):
            place = self.get_params().place_items_dict.get(current_loc)
        else:
            place = self.get_params().place_items_dict.get(u'other')

        if not place:
            return

        if self.get_params().allow_clear_location:
            decor_evts = []
            decorations = []
            for decor_item in self.get_params().allow_clear_location:
                decorations += self.get_game_state().get_objects_by_items([decor_item])

            for decoration in decorations:
                evt = GameSellGameObject(objId=decoration.id)
                decor_evts.append(evt)
                self.get_game_state().remove_object_by_id(decoration.id)

            if decor_evts:
                logger.info(u'Очищаем заданные объекты')
                self.get_events_sender().send_game_pack_events(decor_evts)

        place_obj = self.get_item_reader().get(place)

        # Получаем координаты углов карты и заранее места где нельзя ставить
        crd_top, bad_crd = self.get_coords(current_loc)
        if not crd_top and not bad_crd:
            return

        # вычисляем координаты которые уже заняты
        self.parse_bad_coords(bad_crd)

        evts = []
        crd_list = 1
        while crd_list:
            crd_list = self.get_space(place_obj, bad_crd, crd_top)
            if not crd_list:
                break

            next_id = max(
                [_i.maxGameObjectId for _i in self.get_game_state().get_state().locationInfos] +
                [_m.id for _m in self.get_game_state().get_state().gameObjects]) + 1

            for crd in crd_list:
                if self.get_game_state().get_state().gameMoney > 1000000:
                    buy_event = GameBuyItem(itemId=place_obj.id, objId=long(next_id), x=long(crd[0]), y=long(crd[1]))
                    evts.append(buy_event)

                    self.get_game_state().get_state().gameMoney -= place_obj.buyCoins
                    self.get_game_state().get_state().gameObjects.append(dict2obj({
                        u'item': place,
                        u'y': crd[1],
                        u'x': crd[0],
                        u'type': place_obj.type,
                        u'id': next_id
                    }))
                    next_id += 1

        if evts:
            logger.info(u'Ставим %s %i шт' % (place_obj.name, len(evts)))
            self.get_events_sender().send_game_pack_events(evts)

    def parse_bad_coords(self, bad_crd):
        # перебор объектов на острове
        for go in self.get_game_state().get_state().gameObjects:
            if not hasattr(go, 'item'):
                continue
            x = go.x
            y = go.y

            go_obj = self.get_item_reader().get(go.item)

            for rect in go_obj.rects:
                w = rect.rectW + rect.rectX
                h = rect.rectH + rect.rectY

                for i in xrange(w):
                    y_list = bad_crd.get(x + i, [])

                    for j in xrange(h):
                        if not y + j in y_list:
                            y_list.append(y + j)

                    bad_crd[x + i] = y_list

    @staticmethod
    def get_space(place_obj, bad_crd, crd):
        place_w, place_h = 0, 0
        for rect in place_obj.rects:
            if rect.rectW and rect.rectH:
                place_w = rect.rectW
                place_h = rect.rectH

        space_crd = []

        for i in xrange(crd.get('x1'), crd.get('x2') + 1):
            y_list = bad_crd.get(i, [])
            for j in xrange(crd.get('y1'), crd.get('y2') + 1):
                if j in y_list:
                    continue

                if crd.get('y2') - j < place_h:
                    continue

                good = True
                add = []
                for k in xrange(place_w):
                    k_list = bad_crd.get(i + k, [])
                    for l in xrange(place_h):
                        if j + l in k_list:
                            good = False
                            break
                        else:
                            add.append(k)
                    if not good:
                        break
                if good:
                    for k in xrange(place_w):
                        k_list = bad_crd.get(k + i, [])
                        for l in xrange(place_h):
                            if not l + j in k_list:
                                k_list.append(l + j)
                        bad_crd[k + i] = k_list
                    return [(i, j)]
        return space_crd

    def get_coords(self, location):
        if location in ['isle_dream', 'isle_faith']:
            res_bad = {}
            self.get_bad_dict(res_bad, 12, 16, 14, 16)
            self.get_bad_dict(res_bad, 12, 16, 48, 52)
            self.get_bad_dict(res_bad, 12, 18, 74, 76)
            self.get_bad_dict(res_bad, 40, 82, 74, 76)
            self.get_bad_dict(res_bad, 82, 84, 72, 76)
            self.get_bad_dict(res_bad, 82, 84, 14, 22)
            return {'x1': 12, 'x2': 83, 'y1': 14, 'y2': 75}, res_bad

        elif location in ['main']:
            res_bad = {}
            self.get_bad_dict(res_bad, 48, 62, 12, 48)
            self.get_bad_dict(res_bad, 54, 60, 48, 100)
            self.get_bad_dict(res_bad, 62, 112, 30, 48)
            self.get_bad_dict(res_bad, 12, 62, 0, 12)
            self.get_bad_dict(res_bad, 112, 128, 30, 112)
            return {'x1': 12, 'x2': 127, 'y1': 0, 'y2': 105}, res_bad

        elif location in ['isle_alpha', 'isle_omega', 'isle_scarecrow', 'isle_elephant', 'isle_monster', 'isle_02',
                          'isle_star', 'isle_giant']:
            res_bad = {}
            self.get_bad_dict(res_bad, 10, 12, 10, 12)
            self.get_bad_dict(res_bad, 10, 12, 42, 44)
            self.get_bad_dict(res_bad, 42, 44, 42, 44)
            self.get_bad_dict(res_bad, 42, 44, 10, 12)
            return {'x1': 10, 'x2': 43, 'y1': 10, 'y2': 43}, res_bad

        elif location in ['isle_03', 'isle_x', 'isle_sand', 'isle_desert']:
            res_bad = {}
            self.get_bad_dict(res_bad, 12, 14, 12, 14)
            self.get_bad_dict(res_bad, 32, 44, 72, 76)
            self.get_bad_dict(res_bad, 62, 68, 72, 76)
            return {'x1': 12, 'x2': 65, 'y1': 12, 'y2': 76}, res_bad

        elif location in ['isle_hope', 'isle_scary']:
            res_bad = {}
            self.get_bad_dict(res_bad, 12, 16, 12, 16)
            self.get_bad_dict(res_bad, 48, 50, 12, 16)
            self.get_bad_dict(res_bad, 48, 50, 34, 42)
            self.get_bad_dict(res_bad, 48, 50, 72, 74)
            self.get_bad_dict(res_bad, 12, 20, 72, 74)
            return {'x1': 12, 'x2': 49, 'y1': 12, 'y2': 75}, res_bad

        elif location in ['isle_emerald', 'isle_01']:
            res_bad = {}
            self.get_bad_dict(res_bad, 16, 20, 12, 16)
            self.get_bad_dict(res_bad, 70, 72, 30, 38)
            self.get_bad_dict(res_bad, 70, 72, 70, 72)
            self.get_bad_dict(res_bad, 16, 20, 64, 72)

            return {'x1': 16, 'x2': 71, 'y1': 12, 'y2': 73}, res_bad

        elif location in ['isle_wild', 'isle_mobile', 'isle_small', 'isle_xxl']:
            res_bad = {}
            self.get_bad_dict(res_bad, 8, 12, 6, 8)
            self.get_bad_dict(res_bad, 8, 10, 8, 10)
            self.get_bad_dict(res_bad, 42, 46, 6, 8)
            self.get_bad_dict(res_bad, 42, 46, 8, 10)
            self.get_bad_dict(res_bad, 42, 46, 42, 46)
            self.get_bad_dict(res_bad, 42, 44, 44, 46)
            self.get_bad_dict(res_bad, 8, 10, 44, 46)
            return {'x1': 8, 'x2': 40, 'y1': 6, 'y2': 46}, res_bad

        elif location in ['isle_polar', 'isle_ufo', 'isle_halloween', 'isle_large', 'isle_moon']:  # , 'isle_light']:
            res_bad = {}
            self.get_bad_dict(res_bad, 8, 12, 6, 10)
            self.get_bad_dict(res_bad, 8, 10, 44, 46)
            self.get_bad_dict(res_bad, 42, 46, 44, 46)
            self.get_bad_dict(res_bad, 44, 46, 42, 44)
            self.get_bad_dict(res_bad, 42, 46, 6, 8)
            self.get_bad_dict(res_bad, 44, 46, 8, 10)
            return {'x1': 8, 'x2': 40, 'y1': 6, 'y2': 46}, res_bad

        else:
            return None, None

    @staticmethod
    def get_bad_dict(res, x1, x2, y1, y2):
        for i in xrange(x1, x2):
            y_list = res.get(i, [])
            for j in xrange(y1, y2):
                y_list.append(j)
            res[i] = y_list
        return res

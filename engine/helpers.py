# -*- coding: utf-8 -*-

from datetime import datetime as dt
import logging
import sys

logger = logging.getLogger(__name__)


def timestamp_to_str(timestamp):
    day_timestamp = timestamp
    day = day_timestamp / (24 * 60 * 60 * 1000)
    hour_timestamp = day_timestamp % (24 * 60 * 60 * 1000)
    hour = hour_timestamp / (60 * 60 * 1000)
    min_timestamp = hour_timestamp % (60 * 60 * 1000)
    minute = min_timestamp / (60 * 1000)
    sec_timestamp = min_timestamp % (60 * 1000)
    second = sec_timestamp / (60 * 1000)

    res = []

    if day:
        res.append(u'%i дней' % day)
    if hour:
        res.append(u'%i часов' % hour)
    if minute:
        res.append(u'%i минут' % minute)
    if second:
        res.append(u'%i секунд' % second)

    return res


def get_item_count(item, real_count):
        if item.min:
            if real_count < item.min:
                return 0
            if item.max:
                if real_count >= item.max:
                    return 0
                if item.count:
                    if real_count - item.count < item.min:
                        return 0
                    return long(item.count)
                else:
                    return long(real_count - item.min)
            else:
                if item.count:
                    if real_count < item.count + item.min:
                        return 0
                    return long(item.count)
                else:
                    return long(real_count - item.min)
        else:
            if item.max:
                if real_count >= item.max:
                    return 0
                if item.count:
                    if real_count < item.count:
                        return 0
                    return long(item.count)
                else:
                    return long(item.max - real_count)
            else:
                if item.count:
                    if real_count < item.count:
                        return 0
                    return long(item.count)
                else:
                    return long(real_count)


def prompt_query(choice, show_line=True):
    if len(choice) == 0:
        logger.info(u'Нет такого варианта')

    if show_line:
        print u'*' * 50

    prompt_string = u'%s\n' % u'\n'.join(
        [u'%s: %s' % ((u'  %i' % (index + 1))[-2:] if len(choice) > 9 else u'%i' % (index + 1), option)
         for index, option in enumerate(choice)])

    while True:
        sys.stdout.write(prompt_string)
        user_input = raw_input(u'')
        try:
            selected_index = int(user_input) - 1
            if selected_index in xrange(len(choice)):
                selected = choice[selected_index]
                print u'Выбрали: %s\n' % selected
                return selected_index
            else:
                print u'Нет такого варианта\n'

        except ValueError:
            print u'Введенное значение не явлется числом\n'

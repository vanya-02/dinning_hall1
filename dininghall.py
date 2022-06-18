import random
import time
import requests
from concurrent import futures


class DiningHall:
    def __init__(self, number_of_tables, number_of_waiters, menu):
        self.number_of_tables = number_of_tables
        self.number_of_waiters = number_of_waiters
        self.menu = menu
        self.tables = [Table(i, menu) for i in range(self.number_of_tables)]
        self.waiters = Waiters(self.number_of_waiters)
        self.curr_order_id = 0
    
    def distribute_order(self, order):
        waiter_id = order['waiter_id']
        table_id = order['table_id']
        self.tables[table_id].status = 'free'
        self.waiters.waiters[waiter_id]['status'] = 'free'
        self.waiters.free_waiters += 1
        delivery_time = int(time.time()) - order['pick_up_time']
        return delivery_time
    
    def create_orders(self, number_of_orders):
        for i in range(number_of_orders):
            self.waiters.take_order(self.tables, i)


class Table:
    def __init__(self, table_id, menu, status = 'free'):
        self.table_id = table_id
        self.status = status
        self.menu = menu

    def create_order(self, order_id, waiter_id):
        number_of_items = int(random.randint(1, 10))
        items = [random.randint(1, 10) for _ in range(random.randint(1, number_of_items))]
        priority = random.randint(1, 5)
        max_wait = 0
        for i in items:
            max_wait = max(self.menu[i-1]['preparation-time'], max_wait)
        max_wait *= 1.3
        return {
            'order_id' : order_id,
            'table_id' : self.table_id,
            'waiter_id' : waiter_id,
            'items': items,
            'priority' : priority,
            'max_wait' : max_wait,
            'pick_up_time' : int(time.time())
        }

class Waiters:
    def __init__(self, nr_of_waiters):
        self.waiters = []
        for i in range(nr_of_waiters):
          self.waiters.append({
              'waiter_id' : i,
              'state' : 'free'
          })
        self.free_waiters = nr_of_waiters
        self.order_list = []

    def send_order(self, order):
        time.sleep(order['time_await'])
        del order['time_await']
        requests.post('http://localhost:8080/order', json=order)

    def take_order(self, tables_list, order_id):
        for i in range(len(tables_list)):
            if tables_list[i].status == 'free':
                if self.free_waiters > 0 :
                    found_waiter = False
                    for waiter in self.waiters:
                        if waiter['state'] == 'free' and not found_waiter:
                            free_idx = waiter['waiter_id']
                            found_waiter = True
                    self.waiters[free_idx]['state'] = 'not_free'
                    self.free_waiters -= 1
                    tables_list[i].status = 'waiting_the_order'
                    order = tables_list[i].create_order(order_id, waiter_id=free_idx)
                    order['time_await'] = random.randint(2, 4)
                    self.order_list.append(order)
                    break

from upstox_api.api import *
from pprint import pprint
import os, sys
import KuberConfig as mjp
import pandas as pd

class KuberUtils():

    def __init__(self,myUpstox):
        self.upstoxobj = myUpstox


    """
        Code to get profile details
    """
    def get_profile(self):
        # load user profile to variable
        profile = self.upstoxobj.get_profile()
        return profile

    """
        Code to select Product
    """
    def select_product(self):

        exchange = self.select_exchange()
        product = None
        self.clear_screen()
        while exchange is not None:
            self.upstoxobj.get_master_contract(exchange)
            product = self.find_product(exchange)
            self.clear_screen()
            if product is not None:
                break
            exchange = self.select_exchange()

        return product

    """
        Code to select Exchange
    """
    def select_exchange(self):

        if self.profileObj is None:
            self.load_profile()

        back_to_home_screen = False
        valid_exchange_selected = False

        while not valid_exchange_selected:
            print('** Live quote streaming example **\n')
            for index, item in enumerate(self.profileObj[u'exchanges_enabled']):
                print('%d. %s' % (index + 1, item))
            print('9. Back')
            print('\n')

            selection = input('Select exchange: ')

            try:
                selection = int(selection)
            except ValueError:
                break

            if selection == 9:
                valid_exchange_selected = True
                back_to_home_screen = True
                break

            selected_index = selection - 1

            if 0 <= selected_index < len(self.profileObj[u'exchanges_enabled']):
                valid_exchange_selected = True
                break

        if back_to_home_screen:
            return None

        return self.profileObj[u'exchanges_enabled'][selected_index]

    """
        Code to find product
    """
    def find_product(self,exchange):

        break_symbol = '@'
        found_product = False
        result = None

        while not found_product:
            query = input('Type the symbol that you are looking for. Type %s to go back:  ' % break_symbol)
            if query.lower() == break_symbol:
                found_product = True
                result = None
                break
            results = self.upstoxobj.search_instruments(exchange, query)
            if len(results) == 0:
                print('No results found for [%s] in [%s] \n\n' % (query, exchange))
                break
            else:
                for index, result in enumerate(results):
                    if index > 9:
                        break
                    print('%d. %s' % (index, result.symbol))
                selection = input('Please make your selection. Type %s to go back:  ' % break_symbol)

                if query.lower() == break_symbol:
                    found_product = False
                    result = None
                    break

                try:
                    selection = int(selection)
                except ValueError:
                    found_product = False
                    result = None
                    break

                if 0 <= selection <= 9 and len(results) >= selection + 1:
                    found_product = True
                    result = results[selection]
                    break

                found_product = False

        return result

    """
        Code to get balance
    """
    def get_balance(self):
        return self.upstoxobj.get_balance()

    """
        Code to get positions
    """
    def get_positions(self):
        return self.upstoxobj.get_positions()

    """
        Code to get holdings
    """
    def get_holdings(self):
        return self.upstoxobj.get_holdings()

    """
        Code to get order history
    """
    def get_order_history(self,order_id = None):
        return self.upstoxobj.get_order_history(order_id) #ignore "order_id" to fetch all order details

    """
            Code to check Sell Position
    """
    def CheckPositionSell(self,stock):
        position = pd.DataFrame(self.upstoxobj.get_positions())
        if position.empty:
            return True
        bought = position.loc[position[mjp.NET_QUANTITY] > 0][mjp.FUTURE_CONTRACT].tolist()
        if stock not in bought or not bought:
            return True
        elif stock in bought:
            print("There is already a long position on %s, so not selling" % stock)
            #log.write("There is already a long position on %s, so not selling" % stock)
            return False

    """
        Code to check Buy Position
    """
    def CheckPositionBuy(self,stock):
        position = pd.DataFrame(self.upstoxobj.get_positions())
        if position.empty:
            return True
        sold = position.loc[position[mjp.NET_QUANTITY] < 0][mjp.FUTURE_CONTRACT].tolist()
        if stock not in sold or not sold:
            return True
        elif stock in sold:
            print("There is already a short position on %s, so not buying" % stock)
            #log.write("There is already a short position on %s, so not buying" % stock)
            return False

    """
        Code to get Live Data
    """
    def get_live_feed(self,product, feedType = LiveFeedType.LTP):
        if product is not None:
            return self.upstoxobj.get_live_feed(product, feedType)

    """
        Code to start Web Socket
    """
    def start_socket(self,exchange):

        self.upstoxobj.set_on_quote_update(self.event_handler_quote_update)
        # upstoxobj.get_master_contract('NSE_EQ')
        self.upstoxobj.get_master_contract(exchange)
        try:
            self.upstoxobj.subscribe(self.upstoxobj.get_instrument_by_symbol(exchange, 'TATASTEEL'), LiveFeedType.Full)
        except:
            pass
        try:
            self.upstoxobj.subscribe(self.upstoxobj.get_instrument_by_symbol(exchange, 'RELIANCE'), LiveFeedType.LTP)
        except:
            pass
        self.upstoxobj.start_websocket(False)


    """
        Code for event handler to update quote
    """
    def event_handler_quote_update(self,message):
        pprint("Quote Update: %s" % str(message))

    """
        Code to clear screen
    """
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

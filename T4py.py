import ctypes
import sys
import json
import os

class T4py:
    libt4 = None
    dll_path = ''
    account = ''
    passwd = ''
    ca_path = ''
    ca_passwd = ''
    future_id = ''

    stock_branch, stock_account = '', ''
    fo_branch, fo_account = '', ''

    #set this to False under Windows cmd
    to_utf8 = False

    def __init__(self, account_json_file, config_json_file):
        try:
            self._read_config_json(config_json_file)
            self._read_account_json(account_json_file)
            self.libt4 = ctypes.WinDLL(self.dll_path)
        except:
            print "Open T4 DLL error!"

    def _read_config_json(self, json_file):
        try:
            with open(json_file, 'r') as infile:
                ret = json.load(infile)
            self.future_id = ret['future_id']
            self.dll_path = ret['dll_path']
            self.ca_path = ret['ca_path']

            if not os.path.isfile(self.dll_path) or not os.path.isfile(self.ca_path):
                raise IOError()

        except:
            print "Unexpected error:", sys.exc_info()[0]
            raise


    def _read_account_json(self, json_file):
        try:
            with open(json_file, 'r') as infile:
                ret = json.load(infile)
            self.account = ret['id']
            self.passwd = ret['password']

        except:
            print "Reading account json fails:", sys.exc_info()[0]
            raise

    def init_t4(self):
        init_t4 = self.libt4.init_t4
        init_t4.argtypes = [ctypes.c_char_p] * 3
        init_t4.restype = ctypes.c_char_p
        ret = init_t4(self.account, self.passwd, '').decode('big5')

        if self.to_utf8:
            ret = ret.encode('utf8')
        return ret

    def set_utf8_enabled(self, flag):
        to_utf8 = flag

    def show_version(self):
        show_version = self.libt4.show_version
        show_version.argtypes = []
        show_version.restype = ctypes.c_char_p
        ret = show_version().decode('big5')
        if self.to_utf8:
            ret = ret.encode('utf8')
        return ret

    def logout_t4(self):
        logout_t4 = self.libt4.log_out
        logout_t4.argtypes = []
        logout_t4.restype = ctypes.c_int
        ret = logout_t4()
        if ret:
            print "LOGOUT ERROR"
        return ret

    def show_list(self):
        show_list = self.libt4.show_list
        show_list.restype = ctypes.c_char_p
        ret = show_list()
        ret = ret.decode('big5').encode('utf8')
        return ret

    def get_branch_account(self, type='fo'):
        if type == 'fo':
            if self.fo_branch != '' and self.fo_account != '':
                return self.fo_branch, self.fo_account

        if type == 'stock':
            if self.stock_branch != '' and self.stock_account != '':
                return self.stock_branch, self.stock_account

        branch = None
        account = None
        results = self.show_list()
        for i, result in enumerate(results.split('\n')):
            s = result.split('-')
            if (type=='fo' and len(s[0]) == 7) or \
                (type=='stock' and len(s[0]) == 4):
                branch = s[0].upper()
                account = s[1]

        return branch, account

    def get_response_log(self):
        get_response_log = self.libt4.get_response_log
        get_response_log.restype = ctypes.c_char_p
        ret = get_response_log().decode('big5')
        if self.to_utf8:
            ret = ret.encode('utf8')
        return ret

    def add_acc_ca(self, type='fo'):
        add_acc_ca = self.libt4.add_acc_ca
        add_acc_ca.restype = ctypes.c_char_p
        add_acc_ca.argtypes = [ctypes.c_char_p] * 5

        branch, account = self.get_branch_account(type)
        add_acc_ca_branch = ctypes.c_char_p(branch)
        add_acc_ca_account = ctypes.c_char_p(account)
        add_acc_ca_id = ctypes.c_char_p(self.account)
        add_acc_ca_path = ctypes.c_char_p(self.ca_path)
        add_acc_ca_password = ctypes.c_char_p(self.ca_passwd)
        ret = add_acc_ca(add_acc_ca_branch, add_acc_ca_account, add_acc_ca_id, add_acc_ca_path, add_acc_ca_password).decode('big5')
        if self.to_utf8:
            ret = ret.encode('utf8')
        return ret

    def verify_ca_pass(self, type='fo'):
        verify_ca_pass = self.libt4.verify_ca_pass
        verify_ca_pass.restype = ctypes.c_char_p
        verify_ca_pass.argtypes = [ctypes.c_char_p] * 2

        branch, account = self.get_branch_account(type)
        add_acc_ca_branch = ctypes.c_char_p(branch)
        add_acc_ca_account = ctypes.c_char_p(account)
        ret = verify_ca_pass(add_acc_ca_branch, add_acc_ca_account).decode('big5')
        if self.to_utf8:
            ret = ret.encode('utf8')
        return ret


    def stock_balance_sum(self):
        stock_balance_sum = self.libt4.stock_balance_sum
        stock_balance_sum.restype = ctypes.c_char_p
        stock_balance_sum.argtypes = [ctypes.c_char_p] * 4

        stock_balance_sum_type = ctypes.c_char_p('A')
        stock_balance_sum_action = ctypes.c_char_p('0')

        branch, account = self.get_branch_account('stock')
        stock_balance_sum_branch = ctypes.c_char_p(branch)
        stock_balance_sum_account = ctypes.c_char_p(account)

        ret = stock_balance_sum(branch, account, stock_balance_sum_type, stock_balance_sum_action).decode('big5')
        if self.to_utf8:
            ret = ret.encode('utf8')
        return ret

    # For lot_type: 0 for new lot; 1 for offseting lot; space for auto; 6 for only today
    def buy(price, future_id, amount = "1", IOC_or_ROD = "IOC", lot_type = "0", LMT_or_MKT = "LMT"):
        return _order_future("B", price, future_id, amount, IOC_or_ROD, lot_type, LMT_or_MKT)

    def sell(price, future_id, amount = "1", IOC_or_ROD = "IOC", lot_type = "0", LMT_or_MKT = "LMT"):
        return _order_future("S", price, future_id, amount, IOC_or_ROD, lot_type, LMT_or_MKT)

    def offset_buy(price, future_id, amount = "1", IOC_or_ROD = "IOC", lot_type = "1", LMT_or_MKT = "MKT"):
        return _order_future("B", price, future_id, amount, IOC_or_ROD, lot_type, LMT_or_MKT)

    def offset_sell(price, future_id, amount = "1", IOC_or_ROD = "IOC", lot_type = "1", LMT_or_MKT = "MKT"):
        return _order_future("S", price, future_id, amount, IOC_or_ROD, lot_type, LMT_or_MKT)

    def _order_future(b_or_s, price, future_id, amount, IOC_or_ROD, lot_type, LMT_or_MKT):
        for arg in locals().itervalues():
            if isinstance(arg, str) == False:
                raise Exception("Only string argument(s) are allowed")

        future_order = self.libt4.future_order
        future_order.restype = ctypes.c_char_p
        future_order.argtypes = [ctypes.c_char_p] * 9

        order_buy_or_sell = ctypes.c_char_p(b_or_s.upper())
        order_branch = ctypes.c_char_p(branch)
        order_account = ctypes.c_char_p(account)
        order_future_id = ctypes.c_char_p(future_id.upper())
        order_price = ctypes.c_char_p("0"*(6-len(price)) + price) # 008650, two 0s for padding
        order_amount = ctypes.c_char_p("0"*(3-len(amount)) + amount) # 001, two 0s for padding
        order_price_type = ctypes.c_char_p(LMT_or_MKT)
        order_order_type = ctypes.c_char_p(IOC_or_ROD)
        order_lot_type = ctypes.c_char_p(lot_type)

        ret = future_order(
            order_buy_or_sell,
            order_branch,
            order_account,
            order_future_id,
            order_price,
            order_amount,
            order_price_type,
            order_order_type,
            order_lot_type
        )
        ret = ret.decode('big5')
        if self.to_utf8:
            ret = ret.encode('utf8')
        return ret

    def fo_unsettled_qry(self):
        fo_unsettled_qry = self.libt4.fo_unsettled_qry
        fo_unsettled_qry.restype = ctypes.c_char_p
        fo_unsettled_qry.argtypes = [ctypes.c_char_p] * 11

        fo_unsettled_qry_flag = ctypes.c_char_p('0000')
        fo_unsettled_qry_leng = ctypes.c_char_p('0004')
        fo_unsettled_qry_next = ctypes.c_char_p('0000')
        fo_unsettled_qry_prev = ctypes.c_char_p('0000')
        fo_unsettled_qry_gubn = ctypes.c_char_p('0')
        fo_unsettled_qry_grpname = ctypes.c_char_p('')
        fo_unsettled_qry_type1 = ctypes.c_char_p('0')
        fo_unsettled_qry_type2 = ctypes.c_char_p('0')
        fo_unsettled_qry_timeout = ctypes.c_char_p('1')

        branch, account = self.get_branch_account('fo')
        fo_unsettled_qry_branch = ctypes.c_char_p(branch)
        fo_unsettled_qry_account = ctypes.c_char_p(account)

        ret = fo_unsettled_qry(
                fo_unsettled_qry_flag, fo_unsettled_qry_leng, fo_unsettled_qry_next,
                fo_unsettled_qry_prev, fo_unsettled_qry_gubn, fo_unsettled_qry_grpname,
                fo_unsettled_qry_branch, fo_unsettled_qry_account, fo_unsettled_qry_type1,
                fo_unsettled_qry_type2, fo_unsettled_qry_timeout)

        ret = ret.decode('big5')
        if self.to_utf8:
            ret = ret.encode('utf8')
        return ret

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage 1: python T4py.py <<account.json>> <<config.json>>'
        print 'where account.json as follows:'
        print '    {'
        print '         "id": "A123456789",'
        print '         "password": "mypassword"'
        print '    }'
        print
        print 'and config.json as follows:'
        print '    {'
        print '         "future_id": "MTXD6",'
        print '         "dll_path": "c:/T4/t4.dll",'
        print '         "ca_path": "c:/T4/"'
        print '    }'
        exit()
    else:
        # for Yoshi's testing
        t4 = T4py(sys.argv[1], sys.argv[2])
        t4.set_utf8_enabled(True)
        t4.init_t4(sys.argv[1], sys.argv[2])
        t4.fo_unsettled_qry()

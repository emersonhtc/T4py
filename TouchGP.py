from Tkinter import *
import ttk
import T4py

price_field = None
t4 = None
bors = "Buy"
bors_combo = None
buy_or_sell = None

def init(argv1, argv2):
    # T4
    t4 = T4py.T4py(argv1, argv2)
    t4.set_utf8_enabled(False)
    t4.init_t4()
    print t4.add_acc_ca()
    print t4.verify_ca_pass()

    # GUI
    master = Tk()
    global buy_or_sell
    buy_or_sell = StringVar(master)
    buy_or_sell.set("Buy") # default value
    global bors_combo
    bors_combo = ttk.Combobox(master, textvariable=buy_or_sell, values=["Buy", "Sell"], state='readonly')
    bors_combo.grid(row=0, column=0)
    bors_combo.bind("<<ComboboxSelected>>", bors_newselection)

    Label(master, text="Price").grid(row=0, column=1)
    global price_field
    price_field = Entry(master)
    price_field.pack()
    price_field.grid(row=0, column=2)
    go = Button(master, text="GO!")
    go.grid(row=0, column=3)
    go.bind('<Button-1>', go_event)
    price_field.focus_set()

def buy(price):
    old_lot = t4.blocking_query_lot()
    print 'old lot = ' + str(old_lot)
    ret = buy(price, g.FUTURE_ID, lot_type = " ")
    if ret == None:
        return False

    new_lot = t4.blocking_query_lot()
    print 'new lot = ' + str(new_lot)
    if new_lot < (old_lot + 1):
        return False
    else:
        return True

def sell(price):
    old_lot = t4.blocking_query_lot()
    print 'old lot = ' + str(old_lot)
    ret = t4.sell(price, t4.future_id, lot_type = " ")
    if ret == None:
        return False

    new_lot = t4.blocking_query_lot()
    print 'new lot = ' + str(new_lot)
    if new_lot < (old_lot + 1):
        return False
    else:
        return True

def go_event(event):
    global price_field
    price = price_field.get()
    ret = False
    while ret == False:
        if bors == "Buy":
            ret = buy(price)
        elif bors == "Sell":
            ret = sell(price)

def bors_newselection(event):
    global bors
    global bors_combo
    bors = bors_combo.get()
    print(bors)

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'Usage 1: python TouchGP.py <<account.json>> <<config.json>>'
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
        init(sys.argv[1], sys.argv[2])
        mainloop( )

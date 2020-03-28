def print_banner(string): n = sorted([len(i) for i in string.split('\n')])[::-1][0]; print('\n'.join(['='*n, string, '='*n]))
print_banner("""    WECOMICS [TH] DIG KEY
            BY @PASUNX(GITHUB)""")
        
from wecomics import WeComicsClient, WeComicsActivityBoard, dict_to_class
from tools import AutoExcuteFunction
from getpass import getpass
import traceback
import threading
import time
import sys

FORCE_NO_COLOR = 'NO_COLOR' in sys.argv

try:
    if FORCE_NO_COLOR:
        raise Exception()
    from colorama import init, Fore, Style
    init(convert=True)
except:
    class NullClass:
        @property
        def __getattr__(*args, **kwargs):
            return lambda x: ''
    Style = NullClass()
    Fore = NullClass()

class PRINT_TEXT:
    def __init__(self):
        self.excute_func = AutoExcuteFunction()

    def print(self, ttype, text):
        TTYPES = {
            'SUCCESS': [Style.BRIGHT + Fore.WHITE + "[" + Fore.GREEN + "+" + Fore.WHITE + "][" + Fore.YELLOW, [time.strftime, '%d/%m/%Y %H:%M:%S', time.localtime], Fore.WHITE + "] " + text],
            'INFO': [Style.BRIGHT + Fore.WHITE + "[" + Fore.YELLOW + "*" + Fore.WHITE + "][" + Fore.YELLOW, [time.strftime, '%d/%m/%Y %H:%M:%S', time.localtime], Fore.WHITE + "] " + text],
            'NOT_SUCCESS': [Style.BRIGHT + Fore.WHITE + "[" + Fore.RED + "-" + Fore.WHITE + "][" + Fore.YELLOW, [time.strftime, '%d/%m/%Y %H:%M:%S', time.localtime], Fore.WHITE + "] " + text]
        }
        assert ttype in TTYPES
        self.excute_func.execute([print, [lambda *x: ''.join(['%s' % (i) for i in x]), TTYPES[ttype]]])

print_text = PRINT_TEXT()
print_success = lambda x: print_text.print('SUCCESS', x)
print_info = lambda x: print_text.print('INFO', x)
print_not_success = lambda x: print_text.print('NOT_SUCCESS', x)

def login():
    global wecomics, email, password
    email = ([sys.argv[1], print('Email:', sys.argv[1])][0] if len(sys.argv) > 1 else None) or input('Email: ')
    password = None
    wecomics = WeComicsClient(email + '.auth')
    while wecomics.isLogin() == False:
        try:
            password = getpass('Password: ')
        except KeyboardInterrupt:
            try:
                email = input('\nEmail: ')
            except KeyboardInterrupt:
                break
        try:
            wecomics = WeComicsClient(email, password, email + '.auth')
        except Exception as err:
            print_not_success('%s' % ('Fail to Login please try again' if str(err) == 'login_failure' else err))

    if not wecomics.isLogin():
        exit(0)

    password = wecomics.password if password == None else password

    print_success('Login Successfully')
    print_info('Key Balance: %s' % (wecomics.getKeyBalance().data.remaining))
    print_info('Start dig key')

try:
    login()
except Exception as err:
    try:
        login()
    except Exception as err2:
        print(err, err2)
        input()

while True:
    __execute = {
        1: wecomics.share,
        2: wecomics.fortuneWheel,
        3: wecomics.rockPaperScissors,
        4: wecomics.pickupKey
    }
    test = False
    def dig_key(tried=0):
        global wecomics
        global test
        try:
            last_ttype = None
            activity_board = wecomics.getActivityBoard()
            result = []
            
            if not test:
                #key, res = wecomics.testFortuneWheel()
                #key = getattr(key.data, 'key', None) or getattr(key.data, 'receiveKey', None)
                #result.append(['testFortuneWheel', key, 'key'])
                #print(wecomics.testFortuneWheel())
                #activity_board.data.items.append(dict_to_class({'itemId': 1, 'quota': 1}))
                test = True
            
            for item in activity_board.data.items:
                id = item.itemId
                if id in list(__execute):
                    if item.quota != 0:
                        for i in range(item.quota):
                            ttype = WeComicsActivityBoard._VALUES_TO_NAMES[id]
                            last_ttype = ttype
                            if ttype == 'ROCK_PAPER_SCISSORS':
                                res, _ = __execute[id]()
                                if res.data.win == True:
                                    result.append([ttype, res.data.receiveKey, 'key'])
                            if ttype in 'FORTUNE_WHEEL':
                                res, _ = __execute[id]()
                                result.append([ttype, res.data.key, 'key'])
                            elif ttype == 'SHARE':
                                res = __execute[id]()
                                result.append([ttype, 1, 'key'])
                            elif ttype == 'PICKUP_KEY':
                                res = __execute[id]()
                                result.append([ttype, 2, 'key'])

            if result != []:
                [print_success('Get Key From: %s' % (' '.join([str(x) for x in i]) if isinstance(i, list ) else i)) for i in result]
                print_info('Key Balance: %s' % (wecomics.getKeyBalance().data.remaining))

        except Exception as err:
            #traceback.print_exc()
            if tried < 10:
                wecomics = WeComicsClient(email, password, email + '.auth')
                tried += 1
                if tried > 1:
                    print_not_success(('RETRY(%s), ERROR(%s)' % (tried, err)) + ((', LASTTYPE(%s)' % (last_ttype)) if last_ttype else ''))
                time.sleep(10)
                return dig_key(tried)
            raise Exception(err)

    try:
        dig_key()
    except Exception as err:
        input(err)
    try:
        time.sleep(60*5) # WAIT FIVE MIN
    except KeyboardInterrupt:
        break
        
input()
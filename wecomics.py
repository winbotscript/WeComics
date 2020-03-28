import requests
import dill

PLATFORM = 'NokiaNokia 6.1 Plus'
DEVICE_ID = 'deva/48d61d4a-96d4-3905-9b1c-f6fadd5170bb'
APP_CODE = 'COMICS_102'

def loggedIn(func):
    return lambda *args, **kwargs: func(*args, **kwargs) if args[0].isLogin() else Exception('You must Login to WeComics')

class DictToClass:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            value = dict_to_class(value, key) if isinstance(value, dict) else value
            value = [dict_to_class(i, key) if isinstance(i, dict) else i for i in value] if isinstance(value, list) else value
            #if isinstance(value, list):
            #    print(value)
            setattr(self, key, value)
    def __getitem__(self, key):
        return getattr(self, key, None)
    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, ', '.join('%s=%r' % (key, value) for key, value in self.__dict__.items()))

def dict_to_class(_dict, name='DictToClass'):
    if isinstance(_dict, dict):
        _class = DictToClass(**_dict)
        _class.__class__.__name__ = name
    else:
        _class = _dict
    return _class

class customRequests:
    def __init__(self, callback=lambda x: x):
        self.session = requests.session()
        self.callback = callback
    
    def post(self, *args, **kwargs):
        response = self.session.post(*args, **kwargs)
        return self.callback(response)

class WeComicsActivityBoard:
    _VALUES_TO_NAMES = {
        1: "SHARE",
        2: "FORTUNE_WHEEL",
        3: "ROCK_PAPER_SCISSORS",
        4: "PICKUP_KEY"
    }
    
    _NAMES_TO_VALUES = {
        "SHARE": 1,
        "FORTUNE_WHEEL": 2,
        "ROCK_PAPER_SCISSORS": 3,
        "PICKUP_KEY": 4
    }
    
class WeComicsClient:
    API_URL = {
        'AUTH': 'https://auth-api.wecomics.in.th',
        'USER': 'https://user-api.wecomics.in.th',
        'ACTIVITY': 'https://activity-api.wecomics.in.th'
    }

    headers = {
        'User-Agent': 'Comics/3.0.0.10 (com.ookbee.ookbeecomics.android)'
    }

    def __init__(self, email=None, password=None, authorization=None):
        self.auth_session = customRequests(lambda response: dict_to_class(response.json()))
        if email and not password:
            self.loginWithAuthorization(email)
        elif email and password:
            self.loginWithEmail(email=email, password=password)
        elif authorization:
            self.loginWithAuthorization(authorization=authorization)
        if authorization:
            self.saveAuthorization(authorization=authorization)

    def loginWithEmail(self, email, password):
        response = self.auth_session.post(self.API_URL['AUTH'] + '/api/v1/auth', headers=self.headers, json={'email': email, 'password': password, 'platform': PLATFORM, 'deviceId': DEVICE_ID, 'appCode': APP_CODE})
        #print(response, email, password)
        if response.accountId == 0:
            raise Exception(response.errors[0].code)
        for key, value in response.__dict__.items():
            setattr(self, key, value)
        self.email = email
        self.password = password
        self.loginWithAuthorization(authorization=self.__dict__)

    def loginWithAuthorization(self, authorization):
        retry = hasattr(self, 'accountId')
        if isinstance(authorization, str):
            try:
                authorization = dill.load(open(authorization, 'rb'))
            except Exception as err:
                return err
        authorization = dict_to_class(authorization)
        for key, value in authorization.__dict__.items():
            setattr(self, key, value)
        refreshAuthToken = self.refreshAuthToken()
        if hasattr(refreshAuthToken, 'errors'):
            return self.loginWithEmail(self.email, self.password)
        for key, value in refreshAuthToken.__dict__.items():
            setattr(self, key, value)
        self.headers.update({'Authorization': 'Bearer ' + authorization.accessToken.token})
        self.session = requests.session()
        try:
            self.getDeviceInfo()
        except:
            if retry:
                self.loginWithEmail(self, self.email, self.password)

    def saveAuthorization(self, authorization):
        dill.dump({key: value for key, value in self.__dict__.items() if key in ['accessToken', 'email', 'password', 'refreshToken']}, open(authorization, 'wb'))

    def isLogin(self):
        return getattr(self, 'accountId', 0) != 0

    def refreshAuthToken(self):
        return self.auth_session.post(self.API_URL['AUTH'] + '/api/v1/auth/refreshtoken', json={'accessToken': self.accessToken.token, 'refreshToken': self.refreshToken.strip()})
        
    @loggedIn
    def getDeviceInfo(self):
        return dict_to_class(self.session.get(self.API_URL['AUTH'] + '/api/v1/device/me', headers=self.headers).json(), 'DeviceInfo')

    @loggedIn
    def getKeyBalance(self):
        return dict_to_class(self.session.get(self.API_URL['USER'] + '/api/user/%s/app/%s/keybalancewithbonus' % (self.accountId, APP_CODE), headers=self.headers).json(), 'KeyBalance')

    @loggedIn
    def getActivityBoard(self):
        return dict_to_class(self.session.get(self.API_URL['ACTIVITY'] + '/api/user/%s/app/%s/activityBoard' % (self.accountId, APP_CODE), headers=self.headers).json(), 'ActivityBoard')

    @loggedIn
    def getKeyUsageHistory(self, start=0, length=10):
        return self.session.get(self.API_URL['USER'] + '/api/user/%s/app/%s/usagekeyhistory?start=%s&length=%s' % (self.accountId, APP_CODE, start, length), headers=self.headers).json()#, 'KeyUsageHistory')
        #return dict_to_class(self.session.get(self.API_URL['USER'] + '/api/user/%s/app/%s/usagekeyhistory?start=%s&length=%s' % (self.accountId, APP_CODE, start, length), headers=self.headers).json(), 'KeyUsageHistory')

    @loggedIn
    def pickupKey(self):
        return dict_to_class(self.session.post(self.API_URL['ACTIVITY'] + '/api/user/%s/app/%s/keyactivity/pickupkey/submit' % (self.accountId, APP_CODE), headers=self.headers).json(), 'PickupKey')

    def testFortuneWheel(self):
        response = []
        response.append(dict_to_class({'data': {'receiveKey': 1}}))
        response.append(dict_to_class({'success': True}))
        return response

    @loggedIn
    def fortuneWheel(self):
        response = []
        response.append(dict_to_class(self.session.post(self.API_URL['ACTIVITY'] + '/api/user/%s/app/%s/fortunewheel' % (self.accountId, APP_CODE), headers=self.headers).json(), 'FortuneWheel'))
        transactionId = getattr(response[-1], 'data', dict_to_class({'transactionId': 0})).transactionId
        response.append(dict_to_class(self.session.post(self.API_URL['ACTIVITY'] + '/api/user/%s/app/%s/keyactivity/fortunewheel/submit' % (self.accountId, APP_CODE), headers=self.headers, json={'transactionId': transactionId}).json(), 'FortuneWheel'))
        return response

    @loggedIn
    def rockPaperScissors(self):
        response = []
        self.session.get(self.API_URL['ACTIVITY'] + '/api/user/%s/app/%s/keyactivity/rockpaperscissors' % (self.accountId, APP_CODE), headers=self.headers).json()
        self.session.get(self.API_URL['ACTIVITY'] + '/api/user/%s/app/%s/keyactivity/rockpaperscissors/share' % (self.accountId, APP_CODE), headers=self.headers).json()
        response.append(dict_to_class(self.session.post(self.API_URL['ACTIVITY'] + '/api/user/%s/app/%s/rockpaperscissors/result' % (self.accountId, APP_CODE), headers=self.headers).json(), 'RockPaperScissors'))
        #print(response[-1])
        transactionId = response[-1].data.transactionId
        response.append(dict_to_class(self.session.post(self.API_URL['ACTIVITY'] + '/api/user/%s/app/%s/keyactivity/rockpaperscissors/submit' % (self.accountId, APP_CODE), headers=self.headers, json={'transactionId': transactionId}).json(), 'RockPaperScissors'))
        return response

    @loggedIn
    def share(self):
        self.session.get(self.API_URL['ACTIVITY'] + '/api/user/%s/app/%s/keyactivity/share' % (self.accountId, APP_CODE), headers=self.headers).json()
        return dict_to_class(self.session.post(self.API_URL['ACTIVITY'] + '/api/user/%s/app/%s/keyactivity/share/submit' % (self.accountId, APP_CODE), headers=self.headers, json={'transactionId': ''}).json(), 'Share')

if __name__ == '__main__':
    email = 'lionjet.etm@gmail.com'
    password = '0909511875Aa'
    #wecomics = WeComicsClient(email, password, authorization=email + '.auth')
    wecomics = WeComicsClient(email + '.auth')
    print(wecomics.getKeyUsageHistory(0, 5000))
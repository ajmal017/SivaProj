from upstox_api.api import *
from tempfile import gettempdir
import KuberConfig as mjp


mysession = Session (mjp.API_KEY)
mysession.set_redirect_uri (mjp.REDIRECT_URI)
mysession.set_api_secret (mjp.API_SECRET)
print (mysession.get_login_url())

#second time run this below code
mysession.set_code ("")
access_token = mysession.retrieve_access_token()
print ('Received access_token: %s' % access_token)




class upstoxlogin():
    """
        Login functionality
    """
    def initialize_process(self):
        logged_in = False
        print('Welcome to Upstox API!\n')

        stored_api_key = self.read_key_from_settings('api_key')
        stored_access_token = self.read_key_from_settings('access_token')
        if stored_access_token is not None and stored_api_key is not None:
            print('You already have a stored access token: [%s] paired with API key [%s]' % (
                stored_access_token, stored_api_key))
            print('Do you want to use the above credentials?')
            selection = input('Type N for no, any key for yes:  ')
            if selection.lower() != 'n':
                try:
                    self.myUpstox = Upstox(stored_api_key, stored_access_token)
                    logged_in = True
                except requests.HTTPError as e:
                    print('Sorry, there was an error [%s]. Let''s start over\n\n' % e)

        if logged_in is False:
            stored_api_key = self.read_key_from_settings('api_key')
            if stored_api_key is not None:
                api_key = input('What is your app''s API key [%s]:  ' % stored_api_key)
                if api_key == '':
                    api_key = stored_api_key
            else:
                api_key = input('What is your app''s API key:  ')
            self.write_key_to_settings('api_key', api_key)

            stored_api_secret = self.read_key_from_settings('api_secret')
            if stored_api_secret is not None:
                api_secret = input('What is your app''s API secret [%s]:  ' % stored_api_secret)
                if api_secret == '':
                    api_secret = stored_api_secret
            else:
                api_secret = input('What is your app''s API secret:  ')
                self.write_key_to_settings('api_secret', api_secret)

            stored_redirect_uri = self.read_key_from_settings('redirect_uri')
            if stored_redirect_uri is not None:
                redirect_uri = input('What is your app''s redirect_uri [%s]:  ' % stored_redirect_uri)
                if redirect_uri == '':
                    redirect_uri = stored_redirect_uri
            else:
                redirect_uri = input('What is your app''s redirect_uri:  ')
            self.write_key_to_settings('redirect_uri', redirect_uri)

            self.mySession = Session(api_key)
            self.mySession.set_redirect_uri(redirect_uri)
            self.mySession.set_api_secret(api_secret)

            print('\n')

            print('Great! Now paste the following URL on your browser and type the code that you get in return')
            print('URL: %s\n' % self.mySession.get_login_url())

            input('Press the enter key to continue\n')

            code = input('What is the code you got from the browser:  ')

            self.mySession.set_code(code)
            try:
                access_token = self.mySession.retrieve_access_token()
            except SystemError as se:
                print('Uh oh, there seems to be something wrong. Error: [%s]' % se)
                return
            self.write_key_to_settings('access_token', access_token)
            self.myUpstox = Upstox(api_key, access_token)
        #return (self.mySession,myUpstox)

    """
        Code to write key settings to a file in temporary directory
    """
    def write_key_to_settings(self,key, value):
        filename = os.path.join(gettempdir(), 'interactive_api.json')
        try:
            file = open(filename, 'r')
        except IOError:
            data = {"api_key": "", "api_secret": "", "redirect_uri": "", "access_token": ""}
            with open(filename, 'w') as output_file:
                json.dump(data, output_file)
        file = open(filename, 'r')
        try:
            data = json.load(file)
        except:
            data = {}
        data[key] = value
        with open(filename, 'w') as output_file:
            json.dump(data, output_file)

    """
        Code to read key settings from a file in temporary directory
    """
    def read_key_from_settings(self,key):
        filename = os.path.join(gettempdir(), 'interactive_api.json')
        try:
            file = open(filename, 'r')
        except IOError:
            file = open(filename, 'w')
        file = open(filename, 'r')
        try:
            data = json.load(file)
            return data[key]
        except:
            pass
        return None


import os
import pandas as pd
import asyncio
from pydoll.browser.chromium import Chrome
from pydoll.browser.options import ChromiumOptions
from pydoll.constants import Scripts
from pydoll.constants import Key
from datetime import datetime,timedelta


class RiotAPI_KEYClient:

    def __init__(self, riot_username:str='', riot_password:str=''):

        # nessecary if no key is provided, else we cant get match informations in further process.
        self.riot_username = riot_username
        self.riot_password = riot_password

        # we use a csv to store the key and the path is hard coded to avoid "longer" searches
        self.api_key_file_path = 'D:/Projekte/league_dashboard/functions/api_key/key.csv' # change the key path if needed

        # time check. The API key expires after 24 hours. 
        self.check = False
        if os.path.exists(self.api_key_file_path):
            try:
                self.api_key_data = pd.read_csv(self.api_key_file_path)

                # get the api_key
                self.api_key = self.api_key_data["api_key"].iloc[0]

                self.api_key_time = pd.to_datetime(self.api_key_data["time"].iloc[0])

                current_time = datetime.now()
                time_from_key = self.api_key_time

                if current_time - time_from_key > timedelta(hours = 24):
                    self.check = False
                else:
                    self.check = True
            except ValueError:
                print("Data can't be found!")


        # url to get the api key if no api key found
        self.base_url = 'https://developer.riotgames.com/'

    async def get_api_key(self,headless:bool = False):

        '''
        get_api_key() initializes a bot to retrieve the api_key bound to an account via pydoll.
        The only option to chose from is the headless parameter. This has to be a bool so True of False. False is the standard option but True can be chosen and therefore a Chrome tab will open.
        Do not by any chance interupt the Browser by clicking on anything, especially buttons you can see on the surface. If so the function might not fullfill it's job and will return None instead of a file with the api_key you want to retrieve
        

        Before the function does the job it will check if an api_key already exists and if it's expired to get a new one.

        '''

        
        options = ChromiumOptions()
        options.headless = headless # Option to see what the Bot does. 

        async with Chrome(options=options) as browser:
            tab = await browser.start() # start the browser

            await browser.set_window_maximized()
            tab.mouse.debug = True
            await tab.go_to('https://abrahamjuliot.github.io/creepjs/')
            await asyncio.sleep(1)
            await tab.get_cookies()

            await tab.go_to("https://chatgpt.com")
            await asyncio.sleep(2)
            await tab.get_cookies()


            docs = await browser.new_tab('https://en.wikipedia.org/wiki/Web_scraping')
            await asyncio.sleep(2)
            docs.get_cookies()
            

            await docs.close()

            await tab.go_to(self.base_url)
            await tab.get_cookies()
            await tab.keyboard.press(Key.ENTER)
            await tab.keyboard.press(Key.ENTER)



            await asyncio.sleep(3) # wait a few seconds for the website to load

            button = await tab.find(class_name='navbar-avatar')

            if button: 
                await button.click()
                await asyncio.sleep(2) # wait for the click to happen
                await tab.get_cookies() # collect cookies. very important due to the fact a captcha or recaptcha might appear in a step
                await tab.keyboard.press(Key.ENTER)
                await tab.keyboard.press(Key.ENTER)
                await asyncio.sleep(2)  


                #search the boxes to put username and password in
                username_box = await tab.find(data_testid ='input-username')
                password_box = await tab.find(data_testid = 'input-password')

                if username_box and password_box: # if both were found
                    await asyncio.sleep(5)
                    await username_box.type_text(self.riot_username, humanize=True)# again important to humanize
                    await asyncio.sleep(3) # wait a few seconds because we still have to be human to click 
                    await password_box.type_text(self.riot_password, humanize=True)

                    await asyncio.sleep(1) 

                    #next we need to find the login button
                    await tab.keyboard.press(Key.ENTER)
                    await tab.keyboard.press(Key.ENTER)
                    await tab.keyboard.press(Key.ENTER)
                    await tab.keyboard.press(Key.ENTER)

                    login_btn = await tab.find(data_testid = 'btn-signin-submit')

                    await asyncio.sleep(5)
                    if login_btn: #if we found
                        await login_btn.click() #click the button
                        await asyncio.sleep(10) #again wait, so the website can load. Extra time so everything can load properly


                    await asyncio.sleep(5)




                    await asyncio.sleep(10) # wait till the dashboard of your profile is loaded properly

                    await tab.execute_script("document.body.style.zoom = '0.5'") #problem might arise due to small tab windows.
                                                                                    # then the bot cant see the required button to click, so we zoom out
                    await asyncio.sleep(5)
                    re_iframe = await tab.find(title='reCAPTCHA')

                    if re_iframe:
                        await re_iframe.click() # solves the reCaptcha
                        await asyncio.sleep(10) # wait for proper loading

                        submit= await tab.find(type='submit') #find the submit button of the captcha
                        if submit:
                            await submit.click() # try to submit the captcha
                            await asyncio.sleep(4)
                            # Now we should see the API KEY
                            api_key = await tab.find(id='apikey')
                            if api_key:
                                self.api_key = api_key.get_attribute('value') # this is the api_key
                                self.api_key_time = datetime.now() # get the current time

                            # We got both time and api key. Now construct a dataframe so store the key and time

                                df_api_key = pd.DataFrame({"api_key":self.api_key,
                                                    "time": [self.api_key_time]})
                                self.check = True


                                # Create the file for the api-key in the chosen filepath
                                return df_api_key.to_csv(self.api_key_file_path, index=False)


                            else:
                                return None
                        else:
                            return None
                    else:
                        return None # Captcha couldnt be found
                else:
                    return None

            else:
                return None

        return None

            
    

                    

                




    
    





    
    
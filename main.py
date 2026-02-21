from threading import Thread
from controller.api import run_api
from controller.bot import run_bot

if __name__ == '__main__':
   
    run_api()

    # Start Flask API in a separate thread
    '''
    api_thread = Thread(target=run_api)
    api_thread.daemon = True
    api_thread.start()

    # Start Discord bot in the main thread
    run_bot()
    '''

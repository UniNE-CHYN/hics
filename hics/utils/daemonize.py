import argparse
import time

import redis

def stdmain(cb_launch, cb_add_arguments_to_parser=None):
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--redis", help="Redis URL")
    if cb_add_arguments_to_parser is not None:
        cb_add_arguments_to_parser(parser)
        
    args = parser.parse_args()
    if args.redis is not None:
        redis_client = redis.from_url(args.redis)
    else:
        redis_client = redis.Redis()

    daemon_thread = cb_launch(redis_client, args)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        daemon_thread.stop()    

import threading
import time
from logging import Logger
from redis import Redis

REDIS_CHANNEL_NAME = "casbin-role-watcher"


class RedisWatcherExtended(object):
    """Class that is used by casbin for tracking updates using redis subscriber.
    Update message is called by PyCasbin and Casbin rules are updated on all instances of application."""

    stop_reader_thread = False
    redis_pubsub_connection = None
    logger = None

    def __init__(
        self, logger: Logger, redis_host: str = "redis", redis_port: int = 6379
    ):
        self.redis_url = redis_host
        self.redis_port = redis_port
        self.logger = logger
        self.reader_thread = threading.Thread(target=self.redis_connector_loop)
        self.reader_thread.start()

    def stop_watcher(self):
        """Stopping thread loop and closing redis connection"""
        self.stop_reader_thread = True
        self.reader_thread.join()

    def redis_connector_loop(self):
        """Main loop for redis subscription"""
        initial_delay = 0
        while not self.stop_reader_thread:
            self.redis_update_watch(delay=initial_delay)
            initial_delay = 10

    def redis_update_watch(self, delay=0):
        """Redis subscription loop that monitors changes and executes callback"""
        # in case we want to delay connecting to redis (redis connection failure)
        time.sleep(delay)
        r = Redis(self.redis_url, self.redis_port)
        self.redis_pubsub_connection = r.pubsub()
        self.redis_pubsub_connection.subscribe(REDIS_CHANNEL_NAME)
        self.logger.info("Casbin policy updates watcher is running...")

        while r and not self.stop_reader_thread:
            # wait 20 seconds to see if there is a casbin update
            try:
                message = self.redis_pubsub_connection.get_message(timeout=20)
            except Exception as e:
                self.logger.exception(
                    f"Casbin watcher failed to get message from redis due to: {repr(e)}"
                )
                self.redis_pubsub_connection.close()
                break

            if message and message.get("type") == "message":
                self.logger.debug(
                    f"Casbin policy update identified! Message was: {message}"
                )
                try:
                    self.update_callback()
                except Exception as e:
                    self.logger.exception(
                        f"Casbin watcher failed sending update to piped process due to: {repr(e)}"
                    )
                    self.redis_pubsub_connection.close()
                    break

    def set_update_callback(self, fn):
        """Setting callback method for enforcer model loading"""
        self.update_callback = fn

    def update_callback(self):
        self.logger.critical("Update callback is not overwritten.")

    def update(self):
        """Redis update message publish to channel"""
        r = Redis(self.redis_url, self.redis_port)
        r.publish(
            REDIS_CHANNEL_NAME, f"casbin policy updated at {time.time()}"
        )

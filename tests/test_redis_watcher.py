from unittest import mock

with mock.patch("redis.Redis") as redis:
    from casbin_redis_watcher.watcher import RedisWatcherExtended

redis_published_message = ""
logger = mock.Mock()
REDIS_SERVER = ""
REDIS_PORT = 123


@mock.patch("time.sleep")
def test_redis_connector_loop(sleep):

    mock_return = mock.Mock()
    mock_return.get.return_value = lambda x: mock_get(x)
    redis().pubsub().get_message().return_value = mock_return
    redis().pubsub().get_message.return_value = mock_return

    def mock_get(key):
        if key == "type":
            return "message"

    redis_watcher = RedisWatcherExtended(
        logger=logger, redis_host=REDIS_SERVER, redis_port=REDIS_PORT
    )
    update_mock = mock.Mock()
    redis_watcher.set_update_callback(update_mock)
    redis_watcher.stop_watcher()

    sleep.assert_called()
    redis.assert_called()
    redis().pubsub.assert_called()
    redis().pubsub().subscribe.assert_called()
    redis().pubsub().get_message.assert_called()
    redis().pubsub().get_message().get.assert_called()
    redis().pubsub().get_message().get.assert_called()


def test_redis_watcher_init():
    redis_watcher = RedisWatcherExtended(
        logger=logger, redis_host=REDIS_SERVER, redis_port=REDIS_PORT
    )

    assert redis_watcher.redis_url == REDIS_SERVER
    assert redis_watcher.redis_port == REDIS_PORT
    assert redis_watcher.stop_reader_thread is False
    redis_watcher.stop_watcher()
    assert redis_watcher.stop_reader_thread is True
    assert redis_watcher.logger is not None
    assert redis_watcher.update_callback() is None


def test_default_update_callback():
    redis_watcher = RedisWatcherExtended(
        logger=logger, redis_host=REDIS_SERVER, redis_port=REDIS_PORT
    )
    redis_watcher.stop_watcher()

    update = mock.Mock()
    redis_watcher.set_update_callback(update)
    assert redis_watcher.update_callback is update


def test_update():
    redis_watcher = RedisWatcherExtended(
        logger=logger, redis_host=REDIS_SERVER, redis_port=REDIS_PORT
    )
    redis_watcher.stop_watcher()
    redis_watcher.update()
    redis.assert_called()
    redis().publish.assert_called()

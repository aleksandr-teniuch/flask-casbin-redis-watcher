# Flask-Casbin-Redis-Watcher

Flask-Casbin-Redis-Watcher is a dedicated role watcher for monitoring updates to Casbin policies in Flask applications.

## Credits and Acknowledgements
This project is a continuation and expansion of the original [pycasbin-redis-watcher](https://github.com/ScienceLogic/pycasbin-redis-watcher) by ScienceLogic. Kudos to the original authors for their foundational work.



### Installation
```
pip install flask-casbin-redis-watcher
```

### Basic Usage
Example:
```
from flask_authz import CasbinEnforcer
from casbin_redis_watcher import RedisWatcherExtended

casbin_enforcer = CasbinEnforcer(app, adapter)
watcher = RedisWatcherExtended(CONFIG.REDIS_HOST, CONFIG.REDIS_PORT)
watcher.set_update_callback(casbin_enforcer.load_policy)
casbin_enforcer.set_watcher(watcher)
```

### Using alongside gunicorn 
This redis-watcher module starts separate processes which subscribe to a redis channel, and listens for updates to the casbin policy on that channel. When running within WSGI contexts you may want to start these processes as a postfork action. As is depicted below:
```
from casbin_redis_watcher import RedisWatcherExtended
from sqlalchemy import create_engine
from config import CONFIG
from casbin_sqlalchemy_adapter import Adapter


def post_fork(server, worker):
    engine = create_engine(
        CONFIG.DB_CONNECTION_STR, pool_size=30, max_overflow=50, pool_recycle=1800
    )
    adapter = Adapter(engine)
    
    enforcer = casbin.Enforcer('config/casbinmodel.conf', adapter)
    
    watcher = RedisWatcherExtended(CONFIG.REDIS_HOST, CONFIG.REDIS_PORT)
    watcher.set_update_callback(enforcer.load_policy)
    
    enforcer.set_watcher(watcher)
    
    flask_app = server.app.wsgi()
    flask_app.e = enforcer
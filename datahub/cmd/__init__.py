import eventlet

# NOTE(hieulq): monkey patch eventlet thread for greening.
eventlet.monkey_patch()

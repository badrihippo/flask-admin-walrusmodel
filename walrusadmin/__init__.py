try:
    import walrus
except ImportError:
    raise Exception('Please install walrus in order to use walrus backend')
from .view import ModelView

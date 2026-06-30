from mangum import Mangum

from .app import create

handler = Mangum(create())

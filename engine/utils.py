import hashlib
from pizzamaker.settings import SECRET_KEY


def generate_confirm_code(order):
    key = "{}{}{}".format(SECRET_KEY, order.created_date, order.email)
    return hashlib.sha256(key.encode()).hexdigest()

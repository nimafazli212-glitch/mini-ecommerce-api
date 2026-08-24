class OrderException(Exception):
    pass


class OrderNotFoundException(OrderException):
    pass


class ProductNotFoundException(OrderException):
    pass


class InsufficientStockException(OrderException):
    pass


class InvalidOrderStatusException(OrderException):
    pass
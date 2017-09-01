from typing import TYPE_CHECKING, Callable, Any, List
import re
from nougat.exceptions import ParamRedefineException, ParamMissingException

import logging


class Param:

    def __init__(self,
                 type: Callable[[str], Any],
                 location: (str, List[str]) = None,
                 optional: bool =False,
                 default: Any =None,
                 action: str = None,
                 append: bool = False,
                 description: str = None):

        self.type = type  # type or [type, type]
        self.location = location  # cookies, query, form, headers
        self.optional = optional  # true, false
        self.default = default  # if optional is true
        self.action = action  # rename
        self.append = append  # list or not
        self.description = description  # description

        # location iterable
        if not isinstance(self.location, list):
            self.location = [self.location]


class ParameterGroup:
    pass


class Route:

    def __init__(self, method: str, route: str, controller: Callable) -> None:
        self.method = method.upper()
        self.route = route
        self.controller = controller
        self.params = {}

    def add_param(self,
                  name: str,
                  type: Callable[[str], Any],
                  location: (str, List[str]) = 'query',
                  optional: bool = False,
                  default: Any = None,
                  action=None,
                  append=False,
                  description: str = None
                  ) -> None:

        if name in self.params:
            raise ParamRedefineException(self.route, name)

        self.params[name] = Param(type, location, optional, default, action, append, description)

    def __call__(self, *args, **kwargs):

        raise Exception('Route Function could not be called')

    def match(self, method: str, route: str) -> bool:
        if self.method == method and re.fullmatch(self.route, route):
            return True

        return False


def __method_generator(method: str, route: str) -> Callable:

    def decorator(controller: (Callable, 'Route')) -> 'Route':

        if isinstance(controller, Route):
            controller.method = method
            controller.route = route
            return controller
        else:
            return Route(method, route, controller)

    return decorator


def get(route: str) -> Callable:

    return __method_generator('GET', route)


def post(route: str) -> Callable:

    return __method_generator('POST', route)


def patch(route: str) -> Callable:

    return __method_generator('PATCH', route)


def put(route: str) -> Callable:

    return __method_generator('PUT', route)


def delete(route: str) -> Callable:

    return __method_generator('DELETE', route)


def param(name: str,
          type: Callable[[str], Any],
          location: (str, List[str]) = 'query',
          optional: bool = False,
          default: Any = None,
          action=None,
          append=False,
          description: str = None
          ) -> Callable:

    def decorator(controller: (Callable, 'Route')) -> Route:

        if not isinstance(controller, Route):
            controller = Route('', '', controller)

        controller.add_param(name, type,  location, optional, default, action, append, description)

        return controller

    return decorator


def params(group: 'ParameterGroup') -> Callable:

    def decorator(controller: (Callable, 'Route')):
        if not isinstance(controller, Route):
            controller = Route('', '', controller)

        for attr_name in dir(group):
            attr = getattr(group, attr_name)
            if isinstance(attr, Param):
                controller.add_param(attr_name, attr.type, attr.location, attr.optional, attr.default, attr.action, attr.append, attr.description)

        return controller

    return decorator


class Routing:

    prefix: str = ''

    def __init__(self, request, response):
        self.__request = request
        self.__response = response

    def render(self) -> str:

        pass

    def redirect(self) -> str:

        pass

    def abort(self, code: int, message: str) -> None:
        pass

    def url_for(self):
        pass

    def set_cookies(self) -> None:
        pass

    def set_header(self) -> None:
        pass

    @classmethod
    def routes(cls) -> List[Route]:
        routes: List[Route] = []
        for attr_name in dir(cls):
            attr = getattr(cls, attr_name)
            if isinstance(attr, Route):
                logging.debug("Routing {} has Route {} {}".format(cls.__class__, attr.method, attr.route))
                routes.append(attr)

        return routes

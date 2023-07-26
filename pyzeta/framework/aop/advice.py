"""
TODO.

Authors:\n
- Philipp Schuette\n
"""

from typing import Callable, Generic, Optional, TypeVar

from typing_extensions import Concatenate, ParamSpec

T = TypeVar("T")
P = ParamSpec("P")


class Advice(Generic[T, P]):
    "Class representation of advice, i.e. an action to perform at runtime."

    __slots__ = ("preFunc", "postFunc")

    def __init__(
        self,
        preFunc: Optional[Callable[P, None]] = None,
        postFunc: Optional[Callable[Concatenate[T, P], T]] = None,
    ) -> None:
        """
        Initialize a new advice from callables to be applied around a point
        cut. At least one of the callbacks must be given. The pre callback must
        accept the same arguments as the wrapped method while the post callback
        must additionally accept the return value of the wrapped method as its
        first argument.

        :param preFunc: callback to be invoked before the point cut
        :param postFunc: callback to be invoked after the point cut
        """
        if (not preFunc) and (not postFunc):
            raise ValueError("cannot create advice from two trivial callbacks")
        self.preFunc = preFunc
        self.postFunc = postFunc

    def __call__(self, instanceMethod: Callable[P, T]) -> Callable[P, T]:
        """
        Wrap a given method with the pre and post callbacks of the advice.

        :param instanceMethod: the method to wrap
        :return: the wrapped method
        """

        def wrappedMethod(*args: P.args, **kwargs: P.kwargs) -> T:
            if self.preFunc:
                self.preFunc(*args, **kwargs)
            result = instanceMethod(*args, **kwargs)
            if self.postFunc:
                result = self.postFunc(result, *args, **kwargs)

            return result

        return wrappedMethod

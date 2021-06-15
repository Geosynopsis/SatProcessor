from typing import TypeVar, List

T = TypeVar("T")


class ProviderBase:
    def __init__(self, obj_type: T):
        self.obj_type = obj_type
        self._registry = {}

    def register(self, name: str, obj: T, overwrite=False):
        """Method to register object. If overwrite is true, object with same
        name in the system will be replaced with given object.

        Args:
            name (str): name of object
            obj (T): object to be registered
            overwrite (bool, optional): Defaults to False.

        """
        assert issubclass(
            obj, self.obj_type
        ), f"Only the implementation of {self.obj_type} can be registered"
        if name in self._registry and not overwrite:
            raise ValueError(f"Object with name {name} already exists")
        self._registry[name] = obj

    def deregister(self, name: str) -> T:
        """Removes the object from registry.

        Args:
            name (str): name of object
        """
        del self._registry[name]

    def get(self, name: str) -> T:
        """Retrieves the object with given name from registry

        Args:
            name (str): Name of the object to be retrieved

        Returns:
            T: object for corresponding name in the registry
        """
        if name not in self._registry:
            raise ValueError(
                f"{self.obj_type.__name__} for {name} doesn't exist"
            )
        return self._registry[name]

    @property
    def names(self) -> List[str]:
        """Returns list of all names in the registry

        Returns:
            List[str]: List of all names 
        """
        return list(self._registry.keys())


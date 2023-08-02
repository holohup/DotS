# from abc import ABC, abstractmethod
# from adapters import repository


# class AbstractUOW(ABC):
#     spreads: repository.AbstractRepository

#     def __exit__(self, *args):
#         self.rollback()

#     @abstractmethod
#     def commit(self):
#         raise NotImplementedError

#     @abstractmethod
#     def rollback(self):
#         raise NotImplementedError

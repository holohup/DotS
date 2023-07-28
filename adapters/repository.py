from abc import ABC, abstractmethod

from domain.model import Spread


class AbstractRepository(ABC):
    @abstractmethod
    def add(self, spread: Spread) -> None:
        raise NotImplementedError()

    @abstractmethod
    def get(self, spread_id: str) -> Spread:
        raise NotImplementedError()


class InMemoryRepository(AbstractRepository):
    def __init__(self, spreads: list[Spread]) -> None:
        self._spreads = set(spreads)

    def add(self, spread: Spread) -> None:
        self._spreads.add(spread)

    def get(self, spread_id: str) -> Spread:
        return next(s for s in self._spreads if s.spread_id == spread_id)

    def list(self) -> list[Spread]:
        return list(self._spreads)


# class CsvRepository(AbstractRepository):
#     def __init__(self, folder):
#         self._batches_path = 'batches.csv'
#         self._batches = {}
#         self._load()

#     def get(self, reference):
#         return self._batches.get(reference)

#     def add(self, batch):
#         self._batches[batch.reference] = batch

#     def _load(self):
#         with self._batches_path.open() as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 ref, sku = row['ref'], row['sku']
#                 qty = int(row['qty'])
#                 if row['eta']:
#                     eta = datetime.strptime(row['eta'], '%Y-%m-%d').date()
#                 else:
#                     eta = None
#                 self._batches[ref] = model.Batch(
#                     ref=ref, sku=sku, qty=qty, eta=eta
#                 )
#         if self._allocations_path.exists() is False:
#             return
#         with self._allocations_path.open() as f:
#             reader = csv.DictReader(f)
#             for row in reader:
#                 batchref, orderid, sku = (row['batchref'],)
#                 row['orderid'], row['sku']
#                 qty = int(row['qty'])
#                 line = model.OrderLine(orderid, sku, qty)
#                 batch = self._batches[batchref]
#                 batch._allocations.add(line)

#     def list(self):
#         return list(self._batches.values())

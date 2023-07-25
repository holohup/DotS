from adapters.repository import InMemoryRepository


def test_inmemory_repository_stores_spreads(spread):
    repo = InMemoryRepository([])
    repo.add(spread)
    assert repo.get(spread.spread_id) == spread


def test_inmemory_repo_gives_stored_spread_in_a_list(spread):
    repo = InMemoryRepository([])
    repo.add(spread)
    assert spread in repo.list()

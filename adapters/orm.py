# from sqlalchemy import Column, Integer, MetaData, String, Table,
# create_engine

# from sqlalchemy.orm import registry, sessionmaker

# from domain.model import Spread


# metadata = MetaData()
# mapper_registry = registry()


# spreads_table = Table(
#     'spreads',
#     mapper_registry.metadata,
#     Column('spread_id', Integer, primary_key=True),
#     Column('buy_prices', String(255)),
#     Column('sell_prices', String(255)),
#     Column('max_amount', Integer, nullable=False),
#     Column('open_positions', Integer),
# )
# spreads_table.metadata


# def start_mappers():
#     mapper_registry.map_imperatively(Spread, spreads_table)


# engine = create_engine('sqlite:///DotS.db', echo=True)
# spreads_table.metadata.create_all(bind=engine)
# Session = sessionmaker(bind=engine)
# session = Session()

# start_mappers()

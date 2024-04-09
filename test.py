from datamodel import Listing, OrderDepth, Trade, TradingState, Symbol, Product
from Basic import Trader

timestamp = 1000

listings = {
	"AMETHYSTS": Listing(
		symbol="AMETHYSTS", 
		product="AMETHYSTS", 
		denomination= "SEASHELLS"
	),
	"PRODUCT2": Listing(
		symbol="PRODUCT2", 
		product="PRODUCT2", 
		denomination= "SEASHELLS"
	),
}
first =OrderDepth

first.buy_orders={10: 7, 9: 5}
first.sell_orders={11: -4, 12: -8}

second = OrderDepth
second.buy_orders={142: 3, 141: 5}
second.sell_orders={144: -5, 145: -8}

order_depths = {
	"AMETHYSTS": first,
	"PRODUCT2": second
}

own_trades = {
	"AMETHYSTS": [],
	"PRODUCT2": []
}

market_trades = {
	"AMETHYSTS": [
		Trade(
			symbol="AMETHYSTS",
			price=11,
			quantity=4,
			buyer="",
			seller="",
			timestamp=900
		)
	],
	"PRODUCT2": []
}

position = {
	"AMETHYSTS": 3,
	"PRODUCT2": -5
}

observations = {}
traderData = ""

state = TradingState(
	traderData,
	timestamp,
  listings,
	order_depths,
	own_trades,
	market_trades,
	position,
	observations
)

test = Trader

test.run(test, state)
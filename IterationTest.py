from datamodel import Listing, OrderDepth, Trade, TradingState, Symbol, Product
from firstRound_ver_1_0 import Trader

timestamp = 1000

listings = {
	"AMETHYSTS": Listing(
		symbol="AMETHYSTS", 
		product="AMETHYSTS", 
		denomination= "SEASHELLS"
	),
	"STARFRUIT": Listing(
		symbol="STARFRUIT", 
		product="STARFRUIT", 
		denomination= "SEASHELLS"
	),
}
first =OrderDepth

first.buy_orders={10: 7, 9: 5}
first.sell_orders={11: -4, 12: -8}

second = OrderDepth
second.buy_orders={10001: 3, 345: 14, 20000: 1}
second.sell_orders={1244: -5, 145: -1, 1000145: -8}

order_depths = {
	"AMETHYSTS": second,
	"STARFRUIT": first
}

own_trades = {
	"AMETHYSTS": [],
	"STARFRUIT": []
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
	"STARFRUIT": []
}

position = {
	"AMETHYSTS": 3,
	"STARFRUIT": -5
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
test.run(test, state)
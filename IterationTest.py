from datamodel import Listing, OrderDepth, Trade, TradingState, Symbol, Product
from firstRound_ver_1_8 import Trader

timestamp = 99700

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
second.buy_orders={10001: 3, 9997: 14, 10005: 2, 10002: 7}
second.sell_orders={10002: -5, 9997: -1, 9995: -3, 9999: -5}

order_depths = {
	"AMETHYSTS": second,
	"STARFRUIT": first
}

own_trades = {
	"AMETHYSTS": [
		Trade(
			symbol="AMETHYSTS",
			price=11,
			quantity=4,
			buyer="SUBMISSION",
			seller="",
			timestamp=900
		)],
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
	"AMETHYSTS": 0,
	"STARFRUIT": 0
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

test = Trader()

test.run(state)
test.run(state)
test.run(state)
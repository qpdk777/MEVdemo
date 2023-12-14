import json
import MevBot

initial_balance = '[{"user": "A", "balance": 0.1}, {"user": "B", "balance": 100}, {"user": "C", "balance": 0}, ' \
                  '{"user": "D", "balance": 1357}, {"user": "E", "balance": 8}] '
requests = '[[{"from": "A", "to": "B", "amount": 0.1, "fee": 0}, {"from": "B", "to": "C", "amount": 9, "fee": 1}, ' \
           '{"from": "C", "to": "E", "amount": 9, "fee": 8}], [{"from": "D", "to": "A", "amount": 0.1, "fee": 10}, ' \
           '{"from": "C", "to": "B", "amount": 9, "fee": 2}, {"from": "D", "to": "C", "amount": 200, "fee": 0}], ' \
           '[{"from": "C", "to": "B", "amount": 40, "fee": 20}]] '

bot = MevBot.MevBot(initial_balance)
bot.set_request_list_json(requests)

mev, request_list, transfer_list, user_ending_balance = bot.get_mev(initial_temperature=10000, max_iterations=10000, cooling_rate=0.97)

print("MEV: ", mev)
print("User Balance After Transaction: \n", json.dumps(user_ending_balance, indent=4))
print("Transactions: \n", json.dumps(transfer_list, indent=4))

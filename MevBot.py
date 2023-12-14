import json
import math
from copy import copy, deepcopy
import random


class MevBot:

    def __init__(self, initial_balance_json):
        self.request_list = []
        self.initial_balance_list = json.loads(initial_balance_json)
        self.initial_balance_dict = {}
        self.user_list = []
        for line in self.initial_balance_list:
            self.initial_balance_dict[line['user']] = line['balance']
            self.user_list.append(line['user'])

    def set_request_list_json(self, request_list_json):
        self.request_list = json.loads(request_list_json)
        updated_request_list = []
        for request in self.request_list:
            updated_request = [item for item in request if
                               isinstance(item.get('amount'), (int, float)) and isinstance(item.get('fee'),
                                                                                           (int, float)) and
                               item['amount'] >= 0 and item['fee'] >= 0 and item['from'] in self.user_list and item[
                                   'to'] in self.user_list]
            if updated_request:
                updated_request_list.append(updated_request)

        self.request_list = updated_request_list

    def get_mev(self, initial_temperature=10000, max_iterations=10000, cooling_rate=0.97):
        # simulated annealing
        original_permutation = deepcopy(self.request_list)
        random.shuffle(original_permutation)

        current_permutation = deepcopy(original_permutation)
        current_best_transfer_list = self.find_best_transfer_set(self.initial_balance_dict, current_permutation)
        current_mev = sum(transfer['fee'] for transfer in current_best_transfer_list)

        best_permutation = current_permutation
        best_best_transfer_list = current_best_transfer_list
        best_mev = current_mev

        temperature = initial_temperature

        for iteration in range(max_iterations):
            neighbor_permutation = self.generate_neighbor(current_permutation)
            neighbor_best_transfer_list = self.find_best_transfer_set(self.initial_balance_dict, neighbor_permutation)
            neighbor_mev = sum(transfer['fee'] for transfer in neighbor_best_transfer_list)

            probability = self.acceptance_probability(current_mev, neighbor_mev, temperature)
            if random.random() < probability:
                current_permutation = neighbor_permutation
                current_best_transfer_list = neighbor_best_transfer_list
                current_mev = neighbor_mev

            if current_mev > best_mev:
                best_permutation = current_permutation
                best_best_transfer_list = current_best_transfer_list
                best_mev = current_mev

            temperature *= cooling_rate

        return best_mev, best_permutation, best_best_transfer_list

    @staticmethod
    def generate_neighbor(original_request_list):
        # swap two request at random to generate a neighboring state
        neighbor = original_request_list.copy()
        index1, index2 = random.sample(range(len(neighbor)), 2)
        neighbor[index1], neighbor[index2] = neighbor[index2], neighbor[index1]
        return neighbor

    @staticmethod
    def acceptance_probability(current_energy, new_energy, temperature):
        # calculate the possibility to accept a inferior state
        if new_energy < current_energy:
            return 1.0
        return math.exp((current_energy - new_energy) / temperature)

    @staticmethod
    def simulate_check(initial_balance_dict, transfer_list, selected_transaction_index_list,
                       extra_transaction_index):
        # simulate the transactions to check if it is legal
        current_balance_dict = initial_balance_dict.copy()
        for index, transfer in enumerate(transfer_list):
            if index in selected_transaction_index_list or index == extra_transaction_index:
                current_balance_dict[transfer['from']] -= transfer['amount'] + transfer['fee']
                current_balance_dict[transfer['to']] += transfer['amount']
                if current_balance_dict[transfer['from']] < 0:
                    return False
        return True

    @staticmethod
    def find_best_transfer_set(initial_balance_dict, request_list):
        transfer_list = []
        for request in request_list:
            for transfer in request:
                transfer_list.append(transfer)
        raw_transfer_list = deepcopy(transfer_list)

        selected_transaction_index_list = []

        # find users with sufficient fund to send all transactions
        user_to_total_expense_dict = {}
        user_with_sufficient_fund_list = []
        for user in initial_balance_dict.keys():
            user_to_total_expense_dict[user] = 0
        for transfer in transfer_list:
            user_to_total_expense_dict[transfer['from']] += transfer['amount'] + transfer['fee']
        for user in user_to_total_expense_dict.keys():
            if user_to_total_expense_dict[user] <= initial_balance_dict[user]:
                user_with_sufficient_fund_list.append(user)
        for index, transfer in enumerate(transfer_list):
            transfer['index'] = index
            if transfer['from'] in user_with_sufficient_fund_list:
                selected_transaction_index_list.append(index)

        # add transaction with most fee if legal until there is no transaction to add
        while True:
            unselected_transaction_index_list = list(
                set(range(0, len(transfer_list))) - set(selected_transaction_index_list))
            unselected_transfer_list = [transfer_list[i] for i in unselected_transaction_index_list]
            sorted_unselected_transfer_list = sorted(unselected_transfer_list, key=lambda x: x['fee'], reverse=True)
            new_transaction_added = False
            for i, transfer in enumerate(sorted_unselected_transfer_list):
                extra_transaction_index = transfer['index']
                if MevBot.simulate_check(initial_balance_dict, transfer_list, selected_transaction_index_list,
                                         extra_transaction_index):
                    selected_transaction_index_list.append(extra_transaction_index)
                    new_transaction_added = True
                    break
            if not new_transaction_added:
                break

        # return selected transactions
        selected_transaction_index_list.sort()  # noted that here we should use .sort() instead of sorted()
        selected_transfer_list = [raw_transfer_list[i] for i in selected_transaction_index_list]
        return selected_transfer_list


def main():
    with open('test/initial_balance.json', 'r') as file:
        # print(json.loads(file.read()))
        bot = MevBot(file.read())
    # print(bot.initial_balance_dict)
    with open('test/request_list.json') as file:
        # print(json.loads(file.read()))
        bot.set_request_list_json(file.read())
    # bot.find_best_transfer_set(bot.initial_balance_dict, bot.request_list)

    mev, request_list, transfer_list = bot.get_mev()
    print("MEV: ", mev)
    # print(request_list)
    print("Transactions: \n", json.dumps(transfer_list, indent=4))

    pass


if __name__ == '__main__':
    main()

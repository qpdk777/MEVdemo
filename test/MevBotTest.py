import unittest
from context import MevBot
from MevBot import MevBot
import os


class TestMevBot(unittest.TestCase):
    def setUp(self):
        with open('test/initial_balance.json', 'r') as file:
            initial_balance_json = file.read()
        with open('test/request_list.json', 'r') as file:
            request_list_json = file.read()
        self.bot = MevBot(initial_balance_json)
        self.bot.set_request_list_json(request_list_json)

    def test_initialization(self):
        my_initial_balance_json = '[{"user": "A", "balance": 100}, {"user": "B", "balance": 200}]'
        bot = MevBot(my_initial_balance_json)
        self.assertEqual(bot.initial_balance_dict, {'A': 100, 'B': 200})

    def testCanRemoveIllegalValue(self):
        with open('./test/illegal_value.json', 'r') as file:
            illegal_value_json_str = file.read()
            self.bot.set_request_list_json(illegal_value_json_str)
        self.assertEqual(len(self.bot.request_list), 0)
        self.assertIsNotNone(self.bot.request_list)
        for request in self.bot.request_list:
            for transfer in request:
                self.assertTrue(isinstance(transfer.get('amount'), (int, float)))
                self.assertTrue(isinstance(transfer.get('fee'), (int, float)))
                self.assertTrue(transfer['amount'] >= 0)
                self.assertTrue(transfer['fee'] >= 0)
                self.assertTrue(transfer['from'] in self.bot.user_list)
                self.assertTrue(transfer['to'] in self.bot.user_list)

    def test_generate_neighbor(self):
        original_request_list = self.bot.request_list
        neighbor = self.bot.generate_neighbor(original_request_list)
        self.assertNotEqual(original_request_list, neighbor)

    def test_acceptance_probability(self):
        current_energy = 100
        new_energy = 90
        temperature = 1000
        probability = self.bot.acceptance_probability(current_energy, new_energy, temperature)
        self.assertEqual(probability, 1.0)

    def test_simulate_check(self):
        initial_balance_dict = {'A': 100, 'B': 200}
        transfer_list = [{'from': 'A', 'to': 'B', 'amount': 50, 'fee': 5}]
        selected_transaction_index_list = [0]
        extra_transaction_index = 0
        result = MevBot.simulate_check(initial_balance_dict, transfer_list, selected_transaction_index_list,
                                       extra_transaction_index)
        self.assertTrue(result)

    def test_get_mev(self):
        mev, request_list, transfer_list = self.bot.get_mev()
        self.assertIsNotNone(mev)
        self.assertIsNotNone(request_list)
        self.assertIsNotNone(transfer_list)


if __name__ == '__main__':
    unittest.main()
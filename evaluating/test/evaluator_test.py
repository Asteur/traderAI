"""
Created on 08.11.2017

Module for testing of the evaluating component

@author: Jonas Holtkamp
"""
import unittest

from datetime import date, datetime

from model.StockData import StockData
from utils import read_stock_market_data
from evaluating.portfolio_evaluator import PortfolioEvaluator
from model.CompanyEnum import CompanyEnum
from model.Portfolio import Portfolio
from model.StockMarketData import StockMarketData
from predicting.predictor.random_predictor import RandomPredictor
from predicting.predictor.perfect_predictor import PerfectPredictor
from trading.trader.simple_trader import SimpleTrader
from model.trader_actions import SharesOfCompany, TradingActionList


class EvaluatorTest(unittest.TestCase):
    def testReadStockMarketData(self):
        """
        Tests: evaluator_utils.py/read_stock_market_data

        Read "../datasets/[AAPL|GOOG].csv" and check if that happens correctly
        """
        stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B],
                                                   ['1962-2011', '2012-2017'])

        self.assertGreater(len(stock_market_data.market_data), 0)
        self.assertTrue(CompanyEnum.COMPANY_A in stock_market_data.market_data)
        self.assertTrue(CompanyEnum.COMPANY_B in stock_market_data.market_data)

    def testDoTrade(self):
        """
        Tests: SimpleTrader#doTrade

        Reads the available portfolio and stock market data of stock A and executes one trade.
        Checks if the action list is not empty.
        """
        trader = SimpleTrader(PerfectPredictor(CompanyEnum.COMPANY_A), None)
        current_portfolio_value = 0.0  # Dummy value
        portfolio = Portfolio(10000, [], 'Test')
        market_data = read_stock_market_data([CompanyEnum.COMPANY_A], ['1962-2011'])
        trading_action_list = trader.doTrade(portfolio, current_portfolio_value, market_data)

        self.assertTrue(trading_action_list is not None)
        self.assertTrue(trading_action_list.len(), 1)
        self.assertEqual(trading_action_list.get(0).shares.company_enum, CompanyEnum.COMPANY_A)

    def testUpdateAndDraw(self):
        """
        Tests: Evaluator#inspect_over_time

        Creates a portfolio, a stock market data object
        """
        trader = SimpleTrader(RandomPredictor(), RandomPredictor())

        evaluator = PortfolioEvaluator([trader] * 3, draw_results=False)

        full_stock_market_data = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B],
                                                        ['1962-2011', '2012-2017'])

        # Calculate and save the initial total portfolio value (i.e. the cash reserve)
        portfolio1 = Portfolio(50000.0, [], 'portfolio 1')
        portfolio2 = Portfolio(100000.0, [], 'portfolio 2')
        portfolio3 = Portfolio(150000.0, [], 'portfolio 3')

        portfolios_over_time = evaluator.inspect_over_time(full_stock_market_data, [portfolio1, portfolio2, portfolio3],
                                                           evaluation_offset=100)

        last_date = list(portfolios_over_time['portfolio 1'].keys())[-1]
        self.assertEqual(last_date, datetime.strptime('2017-11-06', '%Y-%m-%d').date())

        data_row_lengths = set([len(value_set) for value_set in portfolios_over_time.values()])
        self.assertEqual(len(data_row_lengths), 1)
        self.assertEqual(data_row_lengths.pop(), 100)

    def testReadData_2stocks_2periods(self):
        period1 = '1962-2011'
        period2 = '2012-2017'

        test = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [period1, period2])

        self.assertEqual(len(test.market_data), 2)
        self.assertTrue(CompanyEnum.COMPANY_A in test.market_data.keys())
        self.assertTrue(CompanyEnum.COMPANY_B in test.market_data.keys())

    def testReadData_2stocks_1period(self):
        period1 = '1962-2011'

        test = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [period1])

        self.assertEqual(len(test.market_data), 2)
        self.assertTrue(CompanyEnum.COMPANY_A in test.market_data.keys())
        self.assertTrue(CompanyEnum.COMPANY_B in test.market_data.keys())

    def testReadData_2stocks_noPeriods(self):
        test = read_stock_market_data([CompanyEnum.COMPANY_A, CompanyEnum.COMPANY_B], [])

        self.assertEqual(len(test.market_data), 2)
        self.assertTrue(CompanyEnum.COMPANY_A in test.market_data.keys())
        self.assertTrue(CompanyEnum.COMPANY_B in test.market_data.keys())

    def testReadData_1stock_2periods(self):
        period1 = '1962-2011'
        period2 = '2012-2017'

        test = read_stock_market_data([CompanyEnum.COMPANY_B], [period1, period2])

        self.assertEqual(len(test.market_data), 1)
        self.assertFalse(CompanyEnum.COMPANY_A in test.market_data.keys())
        self.assertTrue(CompanyEnum.COMPANY_B in test.market_data.keys())

    def testReadData_1stock_noPeriods(self):
        test = read_stock_market_data([CompanyEnum.COMPANY_B], [])

        self.assertEqual(len(test.market_data), 1)
        self.assertFalse(CompanyEnum.COMPANY_A in test.market_data.keys())
        self.assertTrue(CompanyEnum.COMPANY_B in test.market_data.keys())


if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(EvaluatorTest)
    unittest.TextTestRunner(verbosity=2).run(suite)

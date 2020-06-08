# -*- coding: utf-8 -*-

from library.daily_crawler import *
import pymysql.cursors
# import numpy as np
from datetime import timedelta
from library.logging_pack import *
from library import cf


MARKET_KOSPI = 0
MARKET_KOSDAQ = 10
from pandas import DataFrame



class simulator_func_mysql():
    def __init__(self, simul_num, op, db_name):
        self.simul_num = int(simul_num)

        # scraper할 때 start date 가져오기 위해서
        if self.simul_num == -1:
            self.date_setting()

        # option이 reset일 경우 실행
        elif op == 'reset':
            self.op = 'reset'
            self.simul_reset = True
            self.variable_setting()
            self.rotate_date()

        # option이 real일 경우 실행(시뮬레이터와 무관)
        elif op == 'real':
            self.op = 'real'
            self.simul_reset = False
            self.db_name = db_name
            self.variable_setting()

        #  option이 continue 일 경우 실행
        elif op == 'continue':
            self.op = 'continue'
            self.simul_reset = False
            self.variable_setting()
            self.rotate_date()
        else:
            print("simul_num or op 어느 것도 만족 하지 못함 simul_num : %s ,op : %s !!", simul_num, op)

    # 마지막으로 구동했던 시뮬레이터의 날짜를 가져온다.
    def get_jango_data_last_date(self):
        sql = "SELECT date from jango_data order by date desc limit 1"
        return self.engine_simulator.execute(sql).fetchall()[0][0]

    # 모든 테이블을 삭제 하는 함수
    def delete_table_data(self):
        print("delete table!!")
        if self.is_simul_table_exist(self.db_name, "all_item_db"):
            sql = "drop table all_item_db"
            self.engine_simulator.execute(sql)
            # 만약 jango data 컬럼을 수정하게 되면 테이블을 삭제하고 다시 생성이 자동으로 되는데 이때 삭제했으면 delete가 안먹힌다. 그래서 확인 후 delete

        if self.is_simul_table_exist(self.db_name, "jango_data"):
            sql = "drop table jango_data"
            self.engine_simulator.execute(sql)

        if self.is_simul_table_exist(self.db_name, "realtime_daily_buy_list"):
            sql = "drop table realtime_daily_buy_list"
            self.engine_simulator.execute(sql)

    # realtime_daily_buy_list 테이블의 check_item컬럼에 특정 종목의 매수 시간을 넣는 함수
    def update_realtime_daily_buy_list(self, code, min_date):
        sql = "update realtime_daily_buy_list set check_item = '%s' where code = '%s'"
        self.engine_simulator.execute(sql % (min_date, code))

    # 시뮬레이션 옵션 설정 함수
    def variable_setting(self):
        # 아래 if문으로 들어가기 전까지의 변수들은 모든 알고리즘에 공통적으로 적용 되는 설정

        # 오늘 날짜를 설정
        self.date_setting()

        # 시뮬레이팅이 끝나는 날짜.
        self.simul_end_date = self.today
        self.use_daily_buy_list = True
        self.use_min = False
        self.start_min = "0900"

        print("self.simul_num!!! ", self.simul_num)

###!@####################################################################################################################
        # 아래 부터는 알고리즘 별로 별도의 설정을 해주는 부분
        if self.simul_num == 1:
            # 시뮬레이팅 시작 일자
            self.simul_start_date = "20190101"

            ######### 알고리즘 선택 #############
            # 매수 리스트 설정 알고리즘 번호
            self.db_to_realtime_daily_buy_list_num = 1
            # 매도 리스트 설정 알고리즘 번호
            self.sell_list_num = 1
            ###################################

            # 초기 투자자금
            self.start_invest_price = 10000000

            # 매수 금액
            self.invest_unit = 1000000

            # 자산 중 최소로 남겨 둘 금액
            self.limit_money = 3000000

            # 익절 수익률 기준치
            self.sell_point = 10

            # 손절 수익률 기준치
            self.losscut_point = -2

            # 실전/모의 봇 돌릴 때 매수하는 순간 종목의 최신 종가 보다 1% 이상 오른 경우 사지 않도록 하는 설정(변경 가능)
            self.invest_limit_rate = 1.01
            # 실전/모의 봇 돌릴 때 매수하는 순간 종목의 최신 종가 보다 -2% 이하로 떨어진 경우 사지 않도록 하는 설정(변경 가능)
            self.invest_min_limit_rate = 0.98

        elif self.simul_num == 2:
            # 시뮬레이팅 시작 일자
            self.simul_start_date = "20190101"

            ######### 알고리즘 선택 #############
            # 매수 리스트 설정 알고리즘 번호
            self.db_to_realtime_daily_buy_list_num = 1
            # 매도 리스트 설정 알고리즘 번호
            self.sell_list_num = 2
            ###################################
            # 초기 투자자금
            self.start_invest_price = 10000000
            # 매수 금액
            self.invest_unit = 1000000
            # 자산 중 최소로 남겨 둘 금액
            self.limit_money = 1000000
            # # 익절 수익률 기준치
            self.sell_point = False
            # 손절 수익률 기준치
            self.losscut_point = -2
            # 실전/모의 봇 돌릴 때 매수하는 순간 종목의 최신 종가 보다 1% 이상 오른 경우 사지 않도록 하는 설정(변경 가능)
            self.invest_limit_rate = 1.01
            # 실전/모의 봇 돌릴 때 매수하는 순간 종목의 최신 종가 보다 -2% 이하로 떨어진 경우 사지 않도록 하는 설정(변경 가능)
            self.invest_min_limit_rate = 0.98


        elif self.simul_num == 3:

            # 시뮬레이팅 시작 일자

            self.simul_start_date = "20190101"

            ######### 알고리즘 선택 #############

            # 매수 리스트 설정 알고리즘 번호

            self.db_to_realtime_daily_buy_list_num = 3

            # 매도 리스트 설정 알고리즘 번호

            self.sell_list_num = 2

            ###################################

            # 초기 투자자금

            self.start_invest_price = 10000000

            # 매수 금액

            self.invest_unit = 3000000

            # 자산 중 최소로 남겨 둘 금액

            self.limit_money = 1000000

            # 익절 수익률 기준치

            self.sell_point = 10

            # 손절 수익률 기준치

            self.losscut_point = -2
            # 실전/모의 봇 돌릴 때 매수하는 순간 종목의 최신 종가 보다 1% 이상 오른 경우 사지 않도록 하는 설정(변경 가능)
            self.invest_limit_rate = 1.01
            # 실전/모의 봇 돌릴 때 매수하는 순간 종목의 최신 종가 보다 -2% 이하로 떨어진 경우 사지 않도록 하는 설정(변경 가능)
            self.invest_min_limit_rate = 0.98

        #########################################################################################################################
        self.db_name_setting()


        if self.op != 'real':
            # database, table 초기화 함수
            self.table_setting()

            # 시뮬레이팅 할 날짜를 가져 오는 함수
            self.get_date_for_simul()

            # 매수 정지 옵션
            self.buy_stop = False

            # 매도를 한 종목들 대상 수익
            self.total_valuation_profit = 0

            # 실제 수익 : 매도를 한 종목들 대상 수익 + 현재 보유 중인 종목들의 수익
            self.sum_valuation_profit = 0

            # 전재산 : 투자금액 + 실제 수익(self.sum_valuation_profit)
            self.total_invest_price = self.start_invest_price

            # 현재 총 투자한 금액
            self.total_purchase_price = 0

            # 현재 투자 가능한 금액(예수금) = (초기자본 + 매도한 종목의 수익) - 현재 총 투자 금액
            self.d2_deposit = self.start_invest_price

            # 일별 정산 함수
            self.check_balance()

            # 매수할때 수수료 한번, 매도할때 전체금액에 세금, 수수료
            self.tax_rate = 0.003
            self.fees_rate = 0.00015

            # 시뮬레이터를 멈춘 지점 부터 다시 돌리기 위해 사용하는 변수(중요X)
            self.simul_reset_lock = False

    # 데이터베이스와 테이블을 세팅하기 위한 함수
    def table_setting(self):
        print("self.simul_reset" + str(self.simul_reset))
        # 시뮬레이터를 초기화 하고 처음부터 구축하기 위한 로직
        if self.simul_reset:
            print("table reset setting !!! ")
            self.init_database()
        # 시뮬레이터를 초기화 하지 않고 마지막으로 끝난 시점 부터 구동하기 위한 로직
        else:
            # self.simul_reset 이 False이고, 시뮬레이터 데이터베이스와, all_item_db 테이블, jango_table이 존재하는 경우 이어서 시뮬레이터 시작
            if self.is_simul_database_exist() and self.is_simul_table_exist(self.db_name,
                                                                            "all_item_db") and self.is_simul_table_exist(self.db_name, "jango_data"):
                self.init_df_jango()
                self.init_df_all_item()
                # 마지막으로 구동했던 시뮬레이터의 날짜를 가져온다.
                self.last_simul_date = self.get_jango_data_last_date()
                print("self.last_simul_date: " + str(self.last_simul_date))
            #    초반에 reset 으로 돌다가 멈춰버린 경우 다시 init 해줘야함
            else:
                print("초반에 reset 으로 돌다가 멈춰버린 경우 다시 init 해줘야함 ! ")
                self.init_database()
                self.simul_reset = True

    # 데이터베이스 초기화 함수
    def init_database(self):
        self.drop_database()
        self.create_database()
        self.init_df_jango()
        self.init_df_all_item()


    # 데이터베이스를 생성하는 함수
    def create_database(self):
        if self.is_simul_database_exist() == False:
            sql = 'CREATE DATABASE %s'
            self.db_conn.cursor().execute(sql % (self.db_name))
            self.db_conn.commit()

    # 데이터베이스를 삭제하는 함수
    def drop_database(self):
        if self.is_simul_database_exist():
            print("drop!!!!")
            sql = "drop DATABASE %s"
            self.db_conn.cursor().execute(sql % (self.db_name))
            self.db_conn.commit()

    # 데이터베이스의 존재 유무를 파악하는 함수.
    def is_simul_database_exist(self):
        sql = "SELECT 1 FROM Information_schema.SCHEMATA WHERE SCHEMA_NAME = '%s'"
        rows = self.engine_daily_buy_list.execute(sql % (self.db_name)).fetchall()
        print("rows : ", rows)
        if len(rows):
            return True
        else:
            return False

    # 오늘 날짜를 설정하는 함수
    def date_setting(self):
        self.today = datetime.datetime.today().strftime("%Y%m%d")
        self.today_detail = datetime.datetime.today().strftime("%Y%m%d%H%M")
        self.today_date_form = datetime.datetime.strptime(self.today, "%Y%m%d").date()

    # DB 이름 세팅 함수
    def db_name_setting(self):
        #
        if self.op == "real":
            self.engine_simulator = create_engine(
                "mysql+mysqldb://" + cf.db_id + ":" + cf.db_passwd + "@" + cf.db_ip + ":" +cf.db_port+ "/" + str(self.db_name),
                encoding='utf-8')

        else:
            # db_name을 setting 한다.
            self.db_name = "simulator" + str(self.simul_num)
            self.engine_simulator = create_engine(
                "mysql+mysqldb://" + cf.db_id + ":" + cf.db_passwd + "@" + cf.db_ip + ":" +cf.db_port+ "/" + str(self.db_name), encoding='utf-8')

        self.engine_daily_craw = create_engine("mysql+mysqldb://" + cf.db_id + ":" + cf.db_passwd + "@" + cf.db_ip + ":" +cf.db_port+ "/daily_craw",
                                               encoding='utf-8')

        self.engine_craw = create_engine("mysql+mysqldb://" + cf.db_id + ":" + cf.db_passwd + "@" + cf.db_ip + ":" +cf.db_port+ "/min_craw",
                                         encoding='utf-8')
        self.engine_daily_buy_list = create_engine(
            "mysql+mysqldb://" + cf.db_id + ":" + cf.db_passwd + "@" + cf.db_ip + ":" +cf.db_port+ "/daily_buy_list", encoding='utf-8')

        self.engine_simul_setting = create_engine(
            "mysql+mysqldb://" + cf.db_id + ":" + cf.db_passwd + "@" + cf.db_ip + ":" +cf.db_port+ "/simul_setting",
            encoding='utf-8')
        # 특정 데이터 베이스가 아닌, mysql 에 접속하는 객체
        self.db_conn = pymysql.connect(host=cf.db_ip, port=int(cf.db_port), user=cf.db_id, password=cf.db_passwd, charset='utf8')

    # 매수 함수
    def invest_send_order(self, date, code, code_name, open_price, yes_close, j):
        # 시작가가 투자하려는 금액 보다 작아야 매수가 가능하기 때문에 아래 조건
        if open_price < self.invest_unit:
            print(code_name , " 매수!!!!!!!!!!!!!!!")

            # 매수를 하게 되면 all_item_db 테이블에 반영을 한다.
            self.db_to_all_item(date, self.df_realtime_daily_buy_list, j,
                                code,
                                code_name, open_price,
                                yes_close)

            # 매수를 성공적으로 했으면 realtime_daily_buy_list 테이블의 check_item 에 매수 시간을 설정
            self.update_realtime_daily_buy_list(code, date)

            # 일별, 분별 정산 함수
            self.check_balance()

    # code명으로 code_name을 가져오는 함수
    def get_name_by_code(self, code):

        sql = "select code_name from stock_item_all where code = '%s'"
        code_name = self.engine_daily_buy_list.execute(sql % (code)).fetchall()
        print(code_name)
        if code_name:
            return code_name[0][0]
        else:
            return False


    # 실제 매수하는 함수
    def auto_trade_stock_realtime(self, min_date, date_rows_today, date_rows_yesterday):
        for j in range(self.len_df_realtime_daily_buy_list):
            if self.jango_check():

                # 종목 코드를 가져온다.
                code = str(self.df_realtime_daily_buy_list.loc[j, 'code']).rjust(6, "0")

                # 종목명을 가져온다.
                code_name = self.df_realtime_daily_buy_list.loc[j, 'code_name']

                # 매수 당일 시작가를 가져온다.
                open_price = self.get_now_open_price_by_date(code, date_rows_today)

                # 어제 종가를 가져온다.
                yes_close = self.get_yes_close_price_by_date(code, date_rows_yesterday)

                # False는 데이터가 없는것
                if code_name == False or open_price == 0 or open_price == False:
                    continue

                # 매수 주문에 들어간다.
                self.invest_send_order(min_date, code, code_name, open_price, yes_close, j)

            else:
                break;

    # 최근 daily_buy_list의 날짜 테이블에서 code에 해당 하는 row만 가져오는 함수
    def get_daily_buy_list_by_code(self, code, date):
        print("get_daily_buy_list_by_code 함수에 들어왔습니다!")

        sql = "select * from `" + date + "` where code = '%s' group by code"

        daily_buy_list = self.engine_daily_buy_list.execute(sql % (code)).fetchall()

        df_daily_buy_list = DataFrame(daily_buy_list,
                                               columns=['index', 'index2', 'date', 'check_item',
                                                        'code', 'code_name', 'd1_diff_rate', 'close', 'open',
                                                        'high', 'low',
                                                        'volume',
                                                        'clo5', 'clo10', 'clo20', 'clo40', 'clo60', 'clo80',
                                                        'clo100', 'clo120',
                                                        "clo5_diff_rate", "clo10_diff_rate", "clo20_diff_rate",
                                                        "clo40_diff_rate", "clo60_diff_rate",
                                                        "clo80_diff_rate", "clo100_diff_rate",
                                                        "clo120_diff_rate",
                                                        'yes_clo5', 'yes_clo10', 'yes_clo20', 'yes_clo40',
                                                        'yes_clo60',
                                                        'yes_clo80',
                                                        'yes_clo100', 'yes_clo120',
                                                        'vol5', 'vol10', 'vol20', 'vol40', 'vol60', 'vol80',
                                                        'vol100', 'vol120'])
        return df_daily_buy_list

    # realtime_daily_buy_list 테이블의 매수 리스트를 가져오는 함수
    def get_realtime_daily_buy_list(self):
        print("get_realtime_daily_buy_list 함수에 들어왔습니다!")

        # 이 부분은 촬영 후 코드를 간소화 했습니다. 조건문 모두 없앴습니다.

        sql = "select * from realtime_daily_buy_list where check_item = '%s' group by code"

        realtime_daily_buy_list = self.engine_simulator.execute(sql % (0)).fetchall()

        self.df_realtime_daily_buy_list = DataFrame(realtime_daily_buy_list,
                                                    columns=['index', 'index2', 'index3', 'date', 'check_item',
                                                             'code', 'code_name', 'd1_diff_rate', 'close', 'open',
                                                             'high', 'low',
                                                             'volume',
                                                             'clo5', 'clo10', 'clo20', 'clo40', 'clo60', 'clo80',
                                                             'clo100', 'clo120',
                                                             "clo5_diff_rate", "clo10_diff_rate", "clo20_diff_rate",
                                                             "clo40_diff_rate", "clo60_diff_rate",
                                                             "clo80_diff_rate", "clo100_diff_rate",
                                                             "clo120_diff_rate",
                                                             'yes_clo5', 'yes_clo10', 'yes_clo20', 'yes_clo40',
                                                             'yes_clo60',
                                                             'yes_clo80',
                                                             'yes_clo100', 'yes_clo120',
                                                             'vol5', 'vol10', 'vol20', 'vol40', 'vol60', 'vol80',
                                                             'vol100', 'vol120'])


        self.len_df_realtime_daily_buy_list = len(self.df_realtime_daily_buy_list)

    # 가장 최근의 daily_buy_list에 담겨 있는 날짜 테이블 이름을 가져오는 함수
    def get_recent_daily_buy_list_date(self):
        sql = "select TABLE_NAME from information_schema.tables where table_schema = 'daily_buy_list' and TABLE_NAME like '%s' order by table_name desc limit 1"
        row = self.engine_daily_buy_list.execute(sql % ("20%%")).fetchall()

        if len(row) == 0:
            return False
        return row[0][0]


    # 여기서 sql문의 date는 반드시 어제 일자여야 한다. -> 어제 일자 기준 반영된 데이터로 종목을 선정해야함.
     ##!@####################################################################################################################################################################################
    # 매수 할 종목의 리스트를 선정 알고리즘
    def db_to_realtime_daily_buy_list(self, date_rows_today, date_rows_yesterday, i):
        # 5 / 20 골든크로스 buy
        if self.db_to_realtime_daily_buy_list_num == 1:
            # orderby는 거래량 많은 순서

            sql = "select * from `" + date_rows_yesterday + "` a where yes_clo20 > yes_clo5 and clo5 > clo20 " \
                                                            "and NOT exists (select null from stock_konex b where a.code=b.code) " \
                                                            "and close < '%s' group by code"
            realtime_daily_buy_list = self.engine_daily_buy_list.execute(sql % (self.invest_unit)).fetchall()


        # 5 / 40 골든크로스 buy
        elif self.db_to_realtime_daily_buy_list_num == 2:
            # orderby는 거래량 많은 순서
            sql = "select * from `" + date_rows_yesterday + "` a where yes_clo40 > yes_clo5 and clo5 > clo40 " \
                                                            "and NOT exists (select null from stock_konex b where a.code=b.code) " \
                                                            "and close < '%s' group by code"
            realtime_daily_buy_list = self.engine_daily_buy_list.execute(sql % (self.invest_unit)).fetchall()


        elif self.db_to_realtime_daily_buy_list_num == 3:
            sql = "select * from `" + date_rows_yesterday + "` a where d1_diff_rate > 1 " \
                                                            "and NOT exists (select null from stock_konex b where a.code=b.code) " \
                                                            "and close < '%s' group by code"
            # 아래 명령을 통해 테이블로 부터 데이터를 가져오면 리스트 형태로 realtime_daily_buy_list 에 담긴다.
            realtime_daily_buy_list = self.engine_daily_buy_list.execute(sql % (self.invest_unit)).fetchall()

        ######################################################################################################################################################################################

        # realtime_daily_buy_list 에 종목이 하나라도 있다면, 즉 매수할 종목이 하나라도 있다면 아래 로직을 들어간다.
        if len(realtime_daily_buy_list) > 0:
            # use_daily_buy_list 라는 옵션은 daily_buy_list라는 테이블을 사용 할 것인지 넣어둔 옵션
            if self.use_daily_buy_list:

                # realtime_daily_buy_list 라는 리스트를 df_realtime_daily_buy_list 라는 데이터프레임으로 변환하는 과정
                # 차이점은 리스트는 컬럼에 대한 개념이 없는데, 데이터프레임은 컬럼이 있다.

                df_realtime_daily_buy_list = DataFrame(realtime_daily_buy_list,
                                                       columns=['index', 'index2', 'date', 'check_item', 'code',
                                                                'code_name', 'd1_diff_rate', 'close', 'open', 'high',
                                                                'low', 'volume',
                                                                'clo5', 'clo10', 'clo20', 'clo40', 'clo60', 'clo80',
                                                                'clo100', 'clo120',
                                                                "clo5_diff_rate", "clo10_diff_rate", "clo20_diff_rate",
                                                                "clo40_diff_rate", "clo60_diff_rate", "clo80_diff_rate",
                                                                "clo100_diff_rate", "clo120_diff_rate",
                                                                'yes_clo5', 'yes_clo10', 'yes_clo20', 'yes_clo40',
                                                                'yes_clo60',
                                                                'yes_clo80',
                                                                'yes_clo100', 'yes_clo120',
                                                                'vol5', 'vol10', 'vol20', 'vol40', 'vol60', 'vol80',
                                                                'vol100', 'vol120'])

            else:
                df_realtime_daily_buy_list = DataFrame(realtime_daily_buy_list,
                                                       columns=['index', 'code', 'date', 'close', 'd1_diff', 'open',
                                                                'high', 'low', 'volume'])

            # lamda 는 한줄로 표현하는 함수식이다. 여기서 int로 param을 보내야 6d ( 정수) 에서 안걸린다.
            df_realtime_daily_buy_list['code'] = df_realtime_daily_buy_list['code'].apply(
                lambda x: "{:0>6d}".format(int(x)))

            # 시뮬레이터의 경우
            if self.op != 'real':
                df_realtime_daily_buy_list['check_item'] = int(0)
                # [to_sql]
                # df_realtime_daily_buy_list 라는 데이터프레임을
                # simulator 데이터베이스의 realtime_daily_buy_list 테이블로 만들어주는 명령
                #
                # ** if_exists 옵션 **
                # # 데이터베이스에 테이블이 존재할 때 수행 동작을 지정한다.
                # 'fail', 'replace', 'append' 중 하나를 사용할 수 있는데 기본값은 'fail'이다.
                # 'fail'은 데이터베이스에 테이블이 있다면 아무 동작도 수행하지 않는다.
                # 'replace'는 테이블이 존재하면 기존 테이블을 삭제하고 새로 테이블을 생성한 후 데이터를 삽입한다.
                # 'append'는 테이블이 존재하면 데이터만을 추가한다.
                df_realtime_daily_buy_list.to_sql('realtime_daily_buy_list', self.engine_simulator, if_exists='replace')

                # 현재 보유 중인 종목은 매수 리스트(realtime_daily_buy_list) 에서 제거 하는 로직
                if self.is_simul_table_exist(self.db_name, "all_item_db"):
                    sql = "delete from realtime_daily_buy_list where code in (select code from all_item_db where sell_date = '%s' or buy_date = '%s' or sell_date = '%s')"
                    # delete는 리턴 값이 없기 때문에 fetchall 쓰지 않는다.
                    self.engine_simulator.execute(sql % (0, date_rows_today, date_rows_today))

                # 최종적으로 realtime_daily_buy_list 테이블에 저장 된 종목들을 가져온다.
                self.get_realtime_daily_buy_list()

            # 모의, 실전 투자 봇 의 경우
            else:
                # check_item 컬럼에 0 으로 setting
                df_realtime_daily_buy_list['check_item'] = int(0)
                df_realtime_daily_buy_list.to_sql('realtime_daily_buy_list', self.engine_simulator, if_exists='replace')

                # 현재 보유 중인 종목들은 삭제
                sql = "delete from realtime_daily_buy_list where code in (select code from possessed_item)"
                self.engine_simulator.execute(sql)

        # 매수할 종목이 없으면, df_realtime_daily_buy_list라는 데이터프레임의 길이를 저장하는
        # len_df_realtime_daily_buy_list에 다가 0을 넣는다.
        else:
            self.len_df_realtime_daily_buy_list = 0



    # 현재의 주가를 all_item_db에 있는 보유한 종목들에 대해서 반영 한다.
    def db_to_all_item_present_price_update(self, code_name, open, clo5, clo10, clo20, clo40, clo60, clo80, clo100,
                                            clo120, volume):
         # update, delete는 반환값 없어서 fetchall 쓰지 않는다
        sql = "update all_item_db set present_price = '%s', clo5 = '%s', clo10 = '%s', clo20 = '%s', clo40 = '%s', clo60 = '%s', clo80 = '%s', clo100 = '%s', clo120 = '%s', volume = '%s' where code_name = '%s' and sell_date = '%s'"
        self.engine_simulator.execute(
            sql % (open, clo5, clo10, clo20, clo40, clo60, clo80, clo100, clo120, volume, code_name,0))


    # jango_data 라는 테이블을 만들기 위한 self.jango 데이터프레임을 생성
    def init_df_jango(self):
        jango_temp = {'id': []}

        self.jango = DataFrame(jango_temp,
                               columns=['date', 'today_earning_rate', 'sum_valuation_profit', 'total_profit',
                                        'today_profit',
                                        'today_profitcut_count', 'today_losscut_count', 'today_profitcut',
                                        'today_losscut',
                                        'd2_deposit', 'total_possess_count', 'today_buy_count', 'today_buy_list_count',
                                        'today_reinvest_count',
                                        'today_cant_reinvest_count',
                                        'total_asset',
                                        'total_invest',
                                        'sum_item_total_purchase', 'total_evaluation', 'today_rate',
                                        'today_invest_price', 'today_reinvest_price',
                                        'today_sell_price', 'volume_limit', 'reinvest_point', 'sell_point',
                                        'max_reinvest_count', 'invest_limit_rate', 'invest_unit',
                                        'rate_std_sell_point', 'limit_money', 'total_profitcut', 'total_losscut',
                                        'total_profitcut_count',
                                        'total_losscut_count', 'loan_money', 'start_kospi_point',
                                        'start_kosdaq_point', 'end_kospi_point', 'end_kosdaq_point',
                                        'today_buy_total_sell_count',
                                        'today_buy_total_possess_count', 'today_buy_today_profitcut_count',
                                        'today_buy_today_profitcut_rate', 'today_buy_today_losscut_count',
                                        'today_buy_today_losscut_rate',
                                        'today_buy_total_profitcut_count', 'today_buy_total_profitcut_rate',
                                        'today_buy_total_losscut_count', 'today_buy_total_losscut_rate',
                                        'today_buy_reinvest_count0_sell_count',
                                        'today_buy_reinvest_count1_sell_count', 'today_buy_reinvest_count2_sell_count',
                                        'today_buy_reinvest_count3_sell_count', 'today_buy_reinvest_count4_sell_count',
                                        'today_buy_reinvest_count4_sell_profitcut_count',
                                        'today_buy_reinvest_count4_sell_losscut_count',
                                        'today_buy_reinvest_count5_sell_count',
                                        'today_buy_reinvest_count5_sell_profitcut_count',
                                        'today_buy_reinvest_count5_sell_losscut_count',
                                        'today_buy_reinvest_count0_remain_count',
                                        'today_buy_reinvest_count1_remain_count',
                                        'today_buy_reinvest_count2_remain_count',
                                        'today_buy_reinvest_count3_remain_count',
                                        'today_buy_reinvest_count4_remain_count',
                                        'today_buy_reinvest_count5_remain_count'],
                               index=jango_temp['id'])

    # all_item_db 라는 테이블을 만들기 위한 self.df_all_item 데이터프레임
    def init_df_all_item(self):
        df_all_item_temp = {'id': []}

        self.df_all_item = DataFrame(df_all_item_temp,
                                     columns=['id', 'order_num', 'code', 'code_name', 'rate', 'purchase_rate',
                                              'purchase_price',
                                              'present_price', 'valuation_price',
                                              'valuation_profit', 'holding_amount', 'buy_date', 'item_total_purchase',
                                              'chegyul_check', 'reinvest_count', 'reinvest_date', 'invest_unit',
                                              'reinvest_unit',
                                              'sell_date', 'sell_price', 'sell_rate', 'rate_std', 'rate_std_mod_val',
                                              'rate_std_htr', 'rate_htr',
                                              'rate_std_mod_val_htr', 'yes_close', 'close', 'd1_diff_rate', 'd1_diff',
                                              'open', 'high',
                                              'low',
                                              'volume', 'clo5', 'clo10', 'clo20', 'clo40', 'clo60', 'clo80',
                                              'clo100', 'clo120', "clo5_diff_rate", "clo10_diff_rate",
                                              "clo20_diff_rate", "clo40_diff_rate", "clo60_diff_rate",
                                              "clo80_diff_rate", "clo100_diff_rate", "clo120_diff_rate"])


    # 가장 초기에 매수 했을 때 all_item_db 에 추가하는 함수

    def db_to_all_item(self, min_date, df, index, code, code_name, purchase_price, yesterday_close):
        self.df_all_item.loc[0, 'code'] = code
        self.df_all_item.loc[0, 'code_name'] = code_name
        # 초기는 반드시 rate가 -0.33 이여야한다. -> 수수료, 세금을 반영함
        self.df_all_item.loc[0, 'rate'] = float(-0.33)

        if yesterday_close:
            self.df_all_item.loc[0, 'purchase_rate'] = round(
                (float(purchase_price) - float(yesterday_close)) / float(yesterday_close) * 100, 2)

        self.df_all_item.loc[0, 'purchase_price'] = purchase_price
        self.df_all_item.loc[0, 'present_price'] = purchase_price

        # #jackbot("code_name: "+ code_name + "purchase_price: "+ str(purchase_price))
        self.df_all_item.loc[0, 'holding_amount'] = int(self.invest_unit / purchase_price)
        self.df_all_item.loc[0, 'buy_date'] = min_date
        self.df_all_item.loc[0, 'item_total_purchase'] = self.df_all_item.loc[0, 'purchase_price'] * \
                                                         self.df_all_item.loc[
                                                             0, 'holding_amount']

        # 실시간으로 오늘 투자한 금액 합산
        self.today_invest_price = self.today_invest_price + self.df_all_item.loc[0, 'item_total_purchase']


        self.df_all_item.loc[0, 'chegyul_check'] = 0
        self.df_all_item.loc[0, 'id'] = 0
        # int로 넣어야 나중에 ++ 할수 있다.
        # self.df_all_item.loc[0, 'reinvest_date'] = '#'
        # self.df_all_item.loc[0, 'reinvest_count'] = int(0)
        # 다음에 투자할 금액은 invest_unit과 같은 금액이다.
        self.df_all_item.loc[0, 'invest_unit'] = self.invest_unit
        # self.df_all_item.loc[0, 'reinvest_unit'] = self.invest_unit

        self.df_all_item.loc[0, 'purchase_rate']

        self.df_all_item.loc[0, 'yes_close'] = yesterday_close
        self.df_all_item.loc[0, 'close'] = df.loc[index, 'close']

        self.df_all_item.loc[0, 'open'] = df.loc[index, 'open']
        self.df_all_item.loc[0, 'high'] = df.loc[index, 'high']
        self.df_all_item.loc[0, 'low'] = df.loc[index, 'low']
        self.df_all_item.loc[0, 'volume'] = df.loc[index, 'volume']

        if self.use_daily_buy_list:
            self.df_all_item.loc[0, 'd1_diff_rate'] = float(df.loc[index, 'd1_diff_rate'])
            self.df_all_item.loc[0, 'clo5'] = df.loc[index, 'clo5']
            self.df_all_item.loc[0, 'clo10'] = df.loc[index, 'clo10']
            self.df_all_item.loc[0, 'clo20'] = df.loc[index, 'clo20']
            self.df_all_item.loc[0, 'clo40'] = df.loc[index, 'clo40']
            self.df_all_item.loc[0, 'clo60'] = df.loc[index, 'clo60']
            self.df_all_item.loc[0, 'clo80'] = df.loc[index, 'clo80']
            self.df_all_item.loc[0, 'clo100'] = df.loc[index, 'clo100']
            self.df_all_item.loc[0, 'clo120'] = df.loc[index, 'clo120']

            if df.loc[index, 'clo5_diff_rate'] is not None:
                self.df_all_item.loc[0, 'clo5_diff_rate'] = float(df.loc[index, 'clo5_diff_rate'])
            if df.loc[index, 'clo10_diff_rate'] is not None:
                self.df_all_item.loc[0, 'clo10_diff_rate'] = float(df.loc[index, 'clo10_diff_rate'])
            if df.loc[index, 'clo20_diff_rate'] is not None:
                self.df_all_item.loc[0, 'clo20_diff_rate'] = float(df.loc[index, 'clo20_diff_rate'])
            if df.loc[index, 'clo40_diff_rate'] is not None:
                self.df_all_item.loc[0, 'clo40_diff_rate'] = float(df.loc[index, 'clo40_diff_rate'])

            if df.loc[index, 'clo60_diff_rate'] is not None:
                self.df_all_item.loc[0, 'clo60_diff_rate'] = float(df.loc[index, 'clo60_diff_rate'])
            if df.loc[index, 'clo80_diff_rate'] is not None:
                self.df_all_item.loc[0, 'clo80_diff_rate'] = float(df.loc[index, 'clo80_diff_rate'])
            if df.loc[index, 'clo100_diff_rate'] is not None:
                self.df_all_item.loc[0, 'clo100_diff_rate'] = float(df.loc[index, 'clo100_diff_rate'])
            if df.loc[index, 'clo120_diff_rate'] is not None:
                self.df_all_item.loc[0, 'clo120_diff_rate'] = float(df.loc[index, 'clo120_diff_rate'])

        self.df_all_item.loc[0, 'valuation_profit'] = int(0)

        # 컬럼 중에 nan 값이 있는 경우 0으로 변경 -> 이렇게 안하면 아래 데이터베이스에 넣을 때
        # AttributeError: 'numpy.int64' object has no attribute 'translate' 에러 발생
        self.df_all_item=self.df_all_item.fillna(0)


        if self.is_simul_table_exist(self.db_name, "all_item_db"):
            self.df_all_item.to_sql('all_item_db', self.engine_simulator, if_exists='append')
        else:
            self.df_all_item.to_sql('all_item_db', self.engine_simulator, if_exists='replace')

    # 보유한 종목들을 가져오는 함수
    # sell_date가 0이면 현재 보유 중인 종목이다. 매도를 할 경우 sell_date에 매도 한 날짜가 찍힌다.
    def get_data_from_possessed_item(self):
        sql = "SELECT code_name from all_item_db where sell_date = '%s'"
        return self.engine_simulator.execute(sql % (0)).fetchall()

    # 보유 종복 수 반환 함수
    def get_count_possessed_item(self):
        sql = "SELECT count(*) from all_item_db where sell_date = '%s'"
        return self.engine_simulator.execute(sql% (0)).fetchall()[0][0]

    # 테이블의 존재 여부를 파악하는 함수
    def is_simul_table_exist(self, db_name, table_name):
        sql = "select 1 from information_schema.tables where table_schema = '%s' and table_name = '%s'"
        rows = self.engine_simulator.execute(sql % (db_name, table_name)).fetchall()
        if len(rows) == 1:
            return True
        else:
            return False

    # 일별, 분별 정산 함수
    def check_balance(self):
        # all_item_db가 없으면 check_balance 함수를 나가라
        if self.is_simul_table_exist(self.db_name, "all_item_db") == False:
            return

        # 총 수익 금액 (종목별 평가 금액 합산)
        sql = "SELECT sum(valuation_profit) from all_item_db"
        self.sum_valuation_profit = self.engine_simulator.execute(sql).fetchall()[0][0]
        print("sum_valuation_profit: " + str(self.sum_valuation_profit))

        # 전재산이라고 보면 된다. 현재 총손익 까지 고려했을 때
        self.total_invest_price = self.start_invest_price + self.sum_valuation_profit

        # 현재 총 투자한 금액 계산
        sql = "select sum(item_total_purchase) from all_item_db where sell_date = '%s'"
        self.total_purchase_price = self.engine_simulator.execute(sql % (0)).fetchall()[0][0]
        if self.total_purchase_price is None:
            self.total_purchase_price = 0

        # 매도를 한 종목들 대상 수익 계산
        sql = "select sum(valuation_profit) from all_item_db where sell_date != '%s'"
        self.total_valuation_profit = self.engine_simulator.execute(sql % (0)).fetchall()[0][0]

        if self.total_valuation_profit is None:
            self.total_valuation_profit = 0
            # 현재 투자 가능한 금액(예수금) = (초기자본 + 매도한 종목의 수익) - 현재 총 투자 금액
        self.d2_deposit = self.start_invest_price + self.total_valuation_profit - self.total_purchase_price




    # 시뮬레이팅 할 날짜를 가져 오는 함수
    # 장이 열렸던 날 들을 self.date_rows 에 담기 위해서 gs글로벌의 date값을 대표적으로 가져온 것
    def get_date_for_simul(self):
        sql = "select date from `gs글로벌` where date >= '%s' and date <= '%s' group by date"
        self.date_rows = self.engine_daily_craw.execute(sql % (self.simul_start_date, self.simul_end_date)).fetchall()


    # daily_buy_list에 일자 테이블이 존재하는지 확인하는 함수
    def is_date_exist(self, date):
        print("is_date_exist 함수에 들어왔습니다!", date)
        sql = "select 1 from information_schema.tables where table_schema ='daily_buy_list' and table_name = '%s'"
        rows = self.engine_daily_buy_list.execute(sql % (date)).fetchall()
        if len(rows) == 1:
            return True
        else:
            return False


    # 잔액 체크 함수, 잔고가 있으면 True를 반환, 없으면 False를 반환
    def jango_check(self):
        if (int(self.d2_deposit) >= (int(self.limit_money) + int(self.invest_unit) * 1.5)):
            return True
        else:
            print("돈부족해서 invest 불가!!!!!!!!")
            return False

    # 출력 함수
    def print_info(self, min_date):
        print("*&*&*&* self.simul_num :" + str(self.simul_num))
        # all_itme_db 테이블이 생성 되어 있으면 보유한 종목 수를 출력
        if self.is_simul_table_exist(self.db_name, "all_item_db"):
            print("보유종목 수 !!: " + str(self.get_count_possessed_item()))




    # 특정 종목의 시작가를 가져오는 함수
    def get_now_open_price_by_date(self, code, date):
        sql = "select open from `" + date + "` where code = '%s' group by code"
        open = self.engine_daily_buy_list.execute(sql % (code)).fetchall()
        if len(open) == 1:
            return open[0][0]
        else:
            return False

    # 특정 종목의 종가를 가져오는 함수
    def get_now_close_price_by_date(self, code, date):
        sql = "select close from `" + date + "` where code = '%s' group by code"
        return_price = self.engine_daily_buy_list.execute(sql % (code)).fetchall()

        if len(return_price) == 1:
            return return_price[0][0]
        else:
            return False

    # 특정 종목의 어제 종가를 가져오는 함수
    def get_yes_close_price_by_date(self, code, date):
        sql = "select close from `" + date + "` where code = '%s' group by code"
        return_price = self.engine_daily_buy_list.execute(sql % (code)).fetchall()

        if len(return_price) == 1:

            return return_price[0][0]
        else:
            return False

    # 종목의 현재 일자에 대한 주가 정보를 가져 오는 함수
    def get_now_price_by_date(self, code_name, date):
        sql = "select open, clo5, clo10, clo20, clo40, clo60, clo80, clo100, clo120, volume from `" + date + "` where code_name = '%s' group by code"
        rows = self.engine_daily_buy_list.execute(sql % (code_name)).fetchall()

        if len(rows) == 1:
            return rows
        else:
            return False

    # 보유 중인 종목들의 주가를 일별로 업데이트 하는 함수
    # all_item_db에서 업데이트를 한다.
    def update_all_db_by_date(self, date):
        print("update_all_db_by_date 함수에 들어왔다!")
        # 현재 보유 중인 종목 들의 code_name 리스트
        possessed_code_name_list = self.get_data_from_possessed_item()
        if len(possessed_code_name_list) == 0:
            print("현재 보유 중인 종목이 없다 !!!!!")
        for j in range(len(possessed_code_name_list)):
            # 현재 주가를 가져오는 함수

            rows = self.get_now_price_by_date(possessed_code_name_list[j][0], date)
            if rows == False:
                continue
            open = rows[0][0]
            clo5 = rows[0][1]
            clo10 = rows[0][2]
            clo20 = rows[0][3]
            clo40 = rows[0][4]
            clo60 = rows[0][5]
            clo80 = rows[0][6]
            clo100 = rows[0][7]
            clo120 = rows[0][8]
            volume = rows[0][9]

            # 만약에 open가에 어떤 값이 있으면(True) 현재 주가를 all_item_db에 반영 하기 위해 아래 함수를 들어간다.
            if open:
                self.db_to_all_item_present_price_update(possessed_code_name_list[j][0], open, clo5, clo10, clo20, clo40,
                                                         clo60, clo80, clo100, clo120, volume)
            else:
                continue

    # 보유 중인 종목들의 주가 이외의 기타 정보들을 업데이트 하는 함수
    def update_all_db_etc(self):
        sql = "update all_item_db set valuation_price = round((present_price  * holding_amount) - item_total_purchase *0.00015 - present_price*holding_amount*0.00315) where sell_date = '%s'"
        self.engine_simulator.execute(sql%(0))
        # update는 반드시 commit 해줘야함 sqlite 만
        # valuation_profit 적용
        # rate 적용 update
        sql = "update all_item_db set rate= round((valuation_price - item_total_purchase)/item_total_purchase*100,2), valuation_profit =  valuation_price - item_total_purchase where sell_date = '%s';"
        self.engine_simulator.execute(sql%(0))


    # 언제 종목을 팔지(익절, 손절) 결정 하는 알고리즘.
    #!@##############################################################################################################################
    def get_sell_list(self):
        print("get_sell_list!!!")
        # 단순히 현재 보유 종목의 수익률이
        # 익절 기준 수익률(self.sell_point) 이 넘거나,
        # 손절 기준 수익률(self.losscut_point) 보다 떨어지면 파는 알고리즘
        if self.sell_list_num == 1:
            # select 할 컬럼은 항상 코드명, 수익률, 매도할 종목의 현재가, 수익(손실)금액
            # sql 첫 번째 라인은 항상 고정
            sql = "SELECT code, rate, present_price,valuation_profit FROM all_item_db WHERE (sell_date = '%s') " \
                  "and (rate>='%s' or rate <= '%s') group by code"
            sell_list = self.engine_simulator.execute(sql % (0,self.sell_point, self.losscut_point)).fetchall()


        # 5 / 20 이동 평균선 데드크로스 이거나, losscut_point(손절 기준 수익률) 이하로 떨어지면 손절하는 알고리즘
        elif self.sell_list_num == 2:
            sql = "SELECT code, rate, present_price,valuation_profit FROM all_item_db WHERE (sell_date = '%s') " \
                  "and ((clo5 < clo20) or rate <= '%s') group by code"
            sell_list = self.engine_simulator.execute(sql % (0,self.losscut_point)).fetchall()


        # 5 / 40 이동 평균선 데드크로스 이거나, losscut_point(손절 기준 수익률) 이하로 떨어지면 손절하는 알고리즘
        elif self.sell_list_num == 3:
            sql = "SELECT code, rate, present_price,valuation_profit FROM all_item_db WHERE (sell_date = '%s') " \
                  "and ((clo5 < clo40) or rate <= '%s') group by code"

            sell_list = self.engine_simulator.execute(sql % (0,self.losscut_point)).fetchall()


        ##################################################################################################################################################################################################################
        else:
            print("self.sell_list_num 설정이 비었다!!!!")

        return sell_list

    # 실제로 매도를 하는 함수 (매도 한 결과를 all_item_db에 반영)
    def sell_send_order(self, min_date, sell_price, sell_rate, code):
        # print("sell send order")
        sql = "UPDATE all_item_db SET sell_date= '%s', sell_price ='%s' ,sell_rate ='%s' WHERE code='%s' and sell_date = '%s' " \
              "ORDER BY buy_date desc LIMIT 1"
        self.engine_simulator.execute(sql % (min_date, sell_price, sell_rate, code,0))
        # 매도 후 정산
        self.check_balance()

    # 매도를 하기 위한 함수
    def auto_trade_sell_stock(self, date):

        # 매도 할 리스트를 가져오는 함수
        sell_list = self.get_sell_list()
        for i in range(len(sell_list)):
            # 코드명
            get_sell_code = sell_list[i][0]
            # 수익률
            get_sell_rate = sell_list[i][1]
            # 종목의 현재 주가
            get_present_price = sell_list[i][2]
            # 수익(손실) 금액 (종목의 순수익, 순손실 금액)
            valuation_profit = sell_list[i][3]

            if get_sell_rate < 0:
                print("손절 매도!!!!$$$$$$$$$$$ 수익: " + str(valuation_profit) + " / 수익률 : " + str(
                    get_sell_rate) + " / 종목코드: " + str(get_sell_code) + " $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

            else:
                print("익절 매도!!!!$$$$$$$$$$$ 수익: " + str(valuation_profit) + " / 수익률 : " + str(
                    get_sell_rate) + " / 종목코드: " + str(get_sell_code) + " $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")

            # 실제로 매도를 하는 함수 (매도 한 결과를 all_item_db에 반영)
            self.sell_send_order(date, get_present_price, get_sell_rate, get_sell_code)


    # 몇개의 주를 살지 계산해주는 함수
    def buy_num_count(self, invest_unit, present_price):
        # jackbot("******************* buy_num_count!!!")
        return int(int(invest_unit) / int(present_price))

    # 금일 수익 계산 함수
    def get_today_profit(self, date):
        # jackbot("******************* get_today_profit!!!")
        sql = "SELECT sum(valuation_profit) from all_item_db where sell_date like '%s'"
        return self.engine_simulator.execute(sql % ("%%" + date + "%%")).fetchall()[0][0]

    # 총 매입금액 계산 함수
    def get_sum_item_total_purchase(self):

        # jackbot("******************* get_sum_item_total_purchase!!!")
        sql = "SELECT sum(item_total_purchase) from all_item_db where sell_date = '%s'"
        rows=self.engine_simulator.execute(sql %(0)).fetchall()[0][0]
        if rows is not None:
            return rows
        else:
            return 0

    # 총평가금액 계산 함수
    def get_sum_valuation_price(self):
        sql = "SELECT sum(valuation_price) from all_item_db where sell_date = '%s'"
        rows = self.engine_simulator.execute(sql %(0)).fetchall()[0][0]
        if rows is not None:
            return rows
        else:
            return 0

    # 오늘 일자 익절 종목 수
    def get_today_profitcut_count(self, date):
        sql = "SELECT count(code) from all_item_db where sell_date like '%s' and sell_rate>='%s'"
        return self.engine_simulator.execute(sql % ("%%" + date + "%%", 0)).fetchall()[0][0]

    # 오늘 일자 손절 종목 수
    def get_today_losscut_count(self, date):
        sql = "SELECT count(code) from all_item_db where sell_date like '%s' and sell_rate<'%s'"
        return self.engine_simulator.execute(sql % ("%%" + date + "%%", 0)).fetchall()[0][0]

    # 오늘 일자 매도금액
    def get_sum_today_sell_price(self, date):
        sql = "SELECT sum(valuation_price) from all_item_db where sell_date like '%s'"
        return self.engine_simulator.execute(sql % ("%%" + date + "%%")).fetchall()[0][0]

    # 오늘 일자 익절 종목 대상 수익
    def get_sum_today_profitcut(self, date):
        sql = "SELECT sum(valuation_profit) from all_item_db where sell_date like '%s' and valuation_profit >= '%s' "
        return self.engine_simulator.execute(sql % ("%%" + date + "%%", 0)).fetchall()[0][0]

    # 오늘 일자 손절 종목 대상 손실 금액
    def get_sum_today_losscut(self, date):
        sql = "SELECT sum(valuation_profit) from all_item_db where sell_date like '%s' and valuation_profit < '%s' "
        return self.engine_simulator.execute(sql % ("%%" + date + "%%", 0)).fetchall()[0][0]

    # 총 익절 종목 대상 수익
    def get_sum_total_profitcut(self):
        sql = "SELECT sum(valuation_profit) from all_item_db where sell_date != 0 and valuation_profit >= '%s' "
        return self.engine_simulator.execute(sql % (0)).fetchall()[0][0]

    # 총 손절 종목 대상 손실 금액
    def get_sum_total_losscut(self):
        sql = "SELECT sum(valuation_profit) from all_item_db where sell_date != 0 and valuation_profit < '%s' "
        return self.engine_simulator.execute(sql % (0)).fetchall()[0][0]

    # 전체 일자 익절한 종목 수
    def get_sum_total_profitcut_count(self):
        # jackbot("******************* get_sum_total_profitcut_count!!!")
        sql = "select count(code) from all_item_db where sell_date != 0 and valuation_profit >= '%s'"
        return self.engine_simulator.execute(sql % (0)).fetchall()[0][0]

    # 전체 일자 손절한 종목 수
    def get_sum_total_losscut_count(self):
        # jackbot("******************* get_sum_total_losscut_count!!!")
        sql = "select count(code) from all_item_db where sell_date != 0 and valuation_profit < '%s' "
        return self.engine_simulator.execute(sql % (0)).fetchall()[0][0]

    # jango_data의 저장 된 일자 반환 함수
    def get_len_jango_data_date(self):

        sql = "select date from jango_data"
        rows = self.engine_simulator.execute(sql).fetchall()

        return len(rows)

    # 총 보유한 종목 수
    def get_total_possess_count(self):
        # jackbot("******************* get_total_possess_count!!!")
        sql = "select count(code) from all_item_db where sell_date = '%s'"
        return self.engine_simulator.execute(sql % (0)).fetchall()[0][0]

    # jango_data 테이블을 만드는 함수
    def db_to_jango(self, date_rows_today):
        # 정산 함수
        self.check_balance()
        if self.is_simul_table_exist(self.db_name, "all_item_db") == False:
            return

        self.jango.loc[0, 'date'] = date_rows_today


        # self.jango.loc[0, 'total_asset'] = self.total_invest_price - self.loan_money
        self.jango.loc[0, 'today_profit'] = self.get_today_profit(date_rows_today)
        self.jango.loc[0, 'sum_valuation_profit'] = self.sum_valuation_profit
        self.jango.loc[0, 'total_profit'] = self.total_valuation_profit

        self.jango.loc[0, 'total_invest'] = self.total_invest_price
        self.jango.loc[0, 'd2_deposit'] = self.d2_deposit
        # 총매입금액
        self.jango.loc[0, 'sum_item_total_purchase'] = self.get_sum_item_total_purchase()

        # 총평가금액
        self.jango.loc[0, 'total_evaluation'] = self.get_sum_valuation_price()
        self.jango.loc[0, 'today_profitcut_count'] = self.get_today_profitcut_count(date_rows_today)
        self.jango.loc[0, 'today_losscut_count'] = self.get_today_losscut_count(date_rows_today)

        self.jango.loc[0, 'today_invest_price'] = float(self.today_invest_price)

        # self.jango.loc[0, 'today_reinvest_price'] = self.today_reinvest_price
        self.jango.loc[0, 'today_sell_price'] = self.get_sum_today_sell_price(date_rows_today)

        # 오늘 기준 수익률 (키움 잔고 상단에 뜨는 수익률) -0.33 (수수료, 세금)
        try:
            self.jango.loc[0, 'today_rate'] = round(
                (float(self.jango.loc[0, 'total_evaluation']) - float(
                    self.jango.loc[0, 'sum_item_total_purchase'])) / float(
                    self.jango.loc[0, 'sum_item_total_purchase']) * 100 - 0.33, 2)
        except ZeroDivisionError as e:
            pass

        # self.jango.loc[0, 'volume_limit'] = self.volume_limit

        # self.jango.loc[0, 'reinvest_point'] = self.reinvest_point
        self.jango.loc[0, 'sell_point'] = self.sell_point
        # self.jango.loc[0, 'max_reinvest_count'] = self.max_reinvest_count
        self.jango.loc[0, 'invest_limit_rate'] = self.invest_limit_rate
        self.jango.loc[0, 'invest_unit'] = self.invest_unit

        self.jango.loc[0, 'limit_money'] = self.limit_money
        self.jango.loc[0, 'total_possess_count'] = self.get_total_possess_count()
        self.jango.loc[0, 'today_buy_list_count'] = self.len_df_realtime_daily_buy_list
        # self.jango.loc[0, 'today_reinvest_count'] = self.get_today_reinvest_count(date_rows_today)
        # self.jango.loc[0, 'today_cant_reinvest_count'] = self.get_today_cant_reinvest_count()

        # 오늘 익절한 금액
        self.jango.loc[0, 'today_profitcut'] = self.get_sum_today_profitcut(date_rows_today)
        # 오늘 손절한 금액
        self.jango.loc[0, 'today_losscut'] = self.get_sum_today_losscut(date_rows_today)

        # 지금까지 총 익절한 금액
        self.jango.loc[0, 'total_profitcut'] = self.get_sum_total_profitcut()

        # 지금까지 총 손절한 금액
        self.jango.loc[0, 'total_losscut'] = self.get_sum_total_losscut()

        # 지금까지 총 익절한놈들
        self.jango.loc[0, 'total_profitcut_count'] = self.get_sum_total_profitcut_count()

        # 지금까지 총 손절한 놈들

        self.jango.loc[0, 'total_losscut_count'] = self.get_sum_total_losscut_count()

        self.jango.loc[0, 'today_buy_count'] = 0
        self.jango.loc[0, 'today_buy_total_sell_count'] = 0
        self.jango.loc[0, 'today_buy_total_possess_count'] = 0

        self.jango.loc[0, 'today_buy_today_profitcut_count'] = 0

        self.jango.loc[0, 'today_buy_today_losscut_count'] = 0
        self.jango.loc[0, 'today_buy_total_profitcut_count'] = 0

        self.jango.loc[0, 'today_buy_total_losscut_count'] = 0
        # self.jango.loc[0, 'today_buy_reinvest_count0_sell_count'] = 0
        #
        # self.jango.loc[0, 'today_buy_reinvest_count1_sell_count'] = 0
        # self.jango.loc[0, 'today_buy_reinvest_count2_sell_count'] = 0
        # self.jango.loc[0, 'today_buy_reinvest_count3_sell_count'] = 0
        # self.jango.loc[0, 'today_buy_reinvest_count4_sell_count'] = 0
        #
        # self.jango.loc[0, 'today_buy_reinvest_count4_sell_profitcut_count'] = 0
        # self.jango.loc[0, 'today_buy_reinvest_count4_sell_losscut_count'] = 0
        #
        # self.jango.loc[0, 'today_buy_reinvest_count5_sell_count'] = 0
        # self.jango.loc[0, 'today_buy_reinvest_count5_sell_profitcut_count'] = 0
        # self.jango.loc[0, 'today_buy_reinvest_count5_sell_losscut_count'] = 0
        #
        # self.jango.loc[0, 'today_buy_reinvest_count0_remain_count'] = 0
        #
        # self.jango.loc[0, 'today_buy_reinvest_count1_remain_count'] = 0
        # self.jango.loc[0, 'today_buy_reinvest_count2_remain_count'] = 0
        # self.jango.loc[0, 'today_buy_reinvest_count3_remain_count'] = 0
        # self.jango.loc[0, 'today_buy_reinvest_count4_remain_count'] = 0
        # self.jango.loc[0, 'today_buy_reinvest_count4_remain_count'] = 0
        # self.jango.loc[0, 'today_buy_reinvest_count5_remain_count'] = 0

        # # 데이터베이스에 테이블이 존재할 때 수행 동작을 지정한다.
        # 'fail', 'replace', 'append' 중 하나를 사용할 수 있는데 기본값은 'fail'이다.
        # 'fail'은 데이터베이스에 테이블이 있다면 아무 동작도 수행하지 않는다.
        # 'replace'는 테이블이 존재하면 기존 테이블을 삭제하고 새로 테이블을 생성한 후 데이터를 삽입한다.
        # 'append'는 테이블이 존재하면 데이터만을 추가한다.
        self.jango.to_sql('jango_data', self.engine_simulator, if_exists='append')

        #     # today_earning_rate
        sql = "update jango_data set today_earning_rate =round(today_profit / total_invest * '%s',2) WHERE date='%s'"
        # rows[i][0] 하는 이유는 rows[i]는 튜플( )로 나온다 그 튜플의 원소를 꺼내기 위해 rows[i]에 [0]을 추가
        self.engine_simulator.execute(sql % (100, date_rows_today))

        len_date = self.get_len_jango_data_date()
        sql = "select date from jango_data"
        rows = self.engine_simulator.execute(sql).fetchall()

        # 위에 전체
        for i in range(len_date):
            # today_buy_count
            sql = "UPDATE jango_data SET today_buy_count=(select count(*) from (select code from all_item_db where buy_date like '%s') b) WHERE date='%s'"
            # date 하는 이유는 rows[i]는 튜플로 나온다 그 튜플의 원소를 꺼내기 위해 [0]을 추가
            self.engine_simulator.execute(sql % ("%%" + str(rows[i][0]) + "%%", rows[i][0]))

            # today_buy_total_sell_count ( 익절, 손절 포함)
            sql = "UPDATE jango_data SET today_buy_total_sell_count=(select count(*) from (select code from all_item_db a where buy_date like '%s' and (a.sell_date != 0) group by code ) b) WHERE date='%s'"
            self.engine_simulator.execute(sql % ("%%" + rows[i][0] + "%%", rows[i][0]))

            # today_buy_total_possess_count 오늘 사고 계속 가지고 있는것들
            sql = "UPDATE jango_data SET today_buy_total_possess_count=(select count(*) from (select code from all_item_db a where buy_date like '%s' and a.sell_date = '%s' group by code ) b) WHERE date='%s'"
            self.engine_simulator.execute(sql % ("%%" + rows[i][0] + "%%", 0, rows[i][0]))

            sql = "UPDATE jango_data SET today_buy_today_profitcut_count=(select count(*) from (select code from all_item_db where buy_date like '%s' and sell_date like '%s' and (sell_rate >= '%s' ) group by code ) b) WHERE date='%s'"
            self.engine_simulator.execute(sql % ("%%" + rows[i][0] + "%%", "%%" + rows[i][0] + "%%", 0, rows[i][0]))


            sql = "UPDATE jango_data SET today_buy_today_profitcut_rate= round(today_buy_today_profitcut_count /today_buy_count *100,2) WHERE date = '%s'"
            self.engine_simulator.execute(sql % (rows[i][0]))

            sql = "UPDATE jango_data SET today_buy_today_losscut_count=(select count(*) from (select code from all_item_db where buy_date like '%s' and sell_date like '%s' and sell_rate < '%s'  group by code ) b) WHERE date='%s'"
            self.engine_simulator.execute(sql % ("%%" + rows[i][0] + "%%", "%%" + rows[i][0] + "%%", 0, rows[i][0]))

            sql = "UPDATE jango_data SET today_buy_today_losscut_rate=round(today_buy_today_losscut_count /today_buy_count *100,2) WHERE date = '%s'"
            self.engine_simulator.execute(sql % (rows[i][0]))

            sql = "UPDATE jango_data SET today_buy_total_profitcut_count=(select count(*) from (select code from all_item_db where buy_date like '%s' and sell_rate >= '%s'  group by code ) b) WHERE date='%s'"
            self.engine_simulator.execute(sql % ("%%" + rows[i][0] + "%%", 0, rows[i][0]))

            sql = "UPDATE jango_data SET today_buy_total_profitcut_rate=round(today_buy_total_profitcut_count /today_buy_count *100,2) WHERE date = '%s'"
            self.engine_simulator.execute(sql % (rows[i][0]))

            sql = "UPDATE jango_data SET today_buy_total_losscut_count=(select count(*) from (select code from all_item_db where buy_date like '%s' and sell_rate < '%s'  group by code ) b) WHERE date='%s'"
            self.engine_simulator.execute(sql % ("%%" + rows[i][0] + "%%", 0, rows[i][0]))

            sql = "UPDATE jango_data SET today_buy_total_losscut_rate=round(today_buy_total_losscut_count/today_buy_count*100,2) WHERE date = '%s'"
            self.engine_simulator.execute(sql % (rows[i][0]))

    # 새로운 종목 매수 및 보유한 종목의 데이터를 업데이트 하는 함수, 매도 함수도 포함
    def trading_by_date(self, date_rows_today,date_rows_yesterday):
        self.print_info(date_rows_today)

        # all_item_db가 존재하고, 현재 보유 중인 종목이 있다면 아래 로직을 들어간다.
        if self.is_simul_table_exist(self.db_name, "all_item_db") and len(self.get_data_from_possessed_item())!=0:
            # 보유 중인 종목들의 주가를 일별로 업데이트 하는 함수
            self.update_all_db_by_date(date_rows_today)
            # 보유 중인 종목들의 주가 이외의 기타 정보들을 업데이트 하는 함수
            self.update_all_db_etc()
            # 매도 함수
            self.auto_trade_sell_stock(date_rows_today)

            # 보유 자산이 있다면, 실제 매수를 한다.
            if self.jango_check():
                # 돈있으면 매수 시작
                self.auto_trade_stock_realtime(str(date_rows_today) + "0900", date_rows_today,date_rows_yesterday)

        #  여긴 가장 초반에 all_itme_db를 만들어야 할때이거나 매수한 종목이 없을 때 들어가는 로직
        else:
            if self.jango_check():
                self.auto_trade_stock_realtime(str(date_rows_today) + "0900", date_rows_today,date_rows_yesterday)

    # 매일 시뮬레이팅 돌기 전 초기화 세팅
    def daily_variable_setting(self):
        self.buy_stop = False
        self.today_invest_price = 0

    # 분별 시뮬레이팅
    def simul_by_min(self,date_rows_today,date_rows_yesterday,i):
        print("**************************   date: " + date_rows_today)
        # 일별 시뮬레이팅 하며 변수 초기화(분별시뮬레이터의 경우도 하루 단위로 초기화)
        self.daily_variable_setting()
        if self.is_date_exist(date_rows_today):
            # 여기 일단 date가 오늘일자다
            self.db_to_realtime_daily_buy_list(date_rows_today,date_rows_yesterday,i)

            self.pytrader_by_min(date_rows_today,date_rows_yesterday)
            self.db_to_jango(date_rows_today)
        else:
            print(date_rows_today + "테이블은 존재하지 않는다!!!")

    # 일별 시뮬레이팅
    def simul_by_date(self, date_rows_today, date_rows_yesterday, i):
        print("**************************   date: " + date_rows_today)
        # 일별 시뮬레이팅 하며 변수 초기화
        self.daily_variable_setting()
        # daily_buy_list에 시뮬레이팅 할 날짜에 해당하는 테이블과 전 날 테이블이 존재하는지 확인
        if self.is_date_exist(date_rows_today) and self.is_date_exist(date_rows_yesterday):
            # 당일 매수 할 종목들을 realtime_daily_buy_list 테이블에 세팅
            self.db_to_realtime_daily_buy_list(date_rows_today, date_rows_yesterday, i)
            # 트레이딩(매수, 매도) 함수 + 보유 종목의 현재가 업데이트 함수
            self.trading_by_date(date_rows_today, date_rows_yesterday)
            # 일별 정산
            self.db_to_jango(date_rows_today)

        else:
            print(date_rows_today + "테이블은 존재하지 않는다!!!")

    # 날짜 별 로테이팅 함수
    def rotate_date(self):
        for i in range(1, len(self.date_rows)):
            # print("self.date_rows!!" ,self.date_rows)
            # 시뮬레이팅 할 일자
            date_rows_today = self.date_rows[i][0]
            # 시뮬레이팅 하기 전의 일자
            date_rows_yesterday = self.date_rows[i - 1][0]

            # self.simul_reset 이 False, 즉 시뮬레이터를 멈춘 지점 부터 실행하기 위한 조건
            if not self.simul_reset and not self.simul_reset_lock:
                if int(date_rows_today) <= int(self.last_simul_date):
                    print("**************************   date: " + date_rows_today + "simul jango date exist pass ! ")
                    continue
                else:
                    self.simul_reset_lock = True

            # 분별 시뮬레이팅
            if self.use_min :
                self.simul_by_min(date_rows_today, date_rows_yesterday, i)
            # 일별 시뮬레이팅
            else:
                self.simul_by_date(date_rows_today, date_rows_yesterday, i)



if __name__ == "__main__":
    # app = QApplication(sys.argv)
    simulator_func_mysql()


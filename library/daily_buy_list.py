#-*- conding: utf-8 -*-
# import open_api
import getpass
from library.daily_crawler import *
# from logging_pack import *
import sys
from library import cf
from pandas import DataFrame
MARKET_KOSPI   = 0
MARKET_KOSDAQ  = 10



class daily_buy_list():
    def __init__(self):
            self.variable_setting()
            #self.daily_buy_list()
            # self.code_update_check()

    # 업데이트가 금일 제대로 끝났는지 확인
    def variable_setting(self):
        self.today = datetime.datetime.today().strftime("%Y%m%d")
        self.today_detail = datetime.datetime.today().strftime("%Y%m%d%H%M")
        self.start_date= cf.start_daily_buy_list
        db_name = "JackBot_daily.db"
        daily_craw_db_name = "daily_craw.db"
        daily_buy_list_db_name = "daily_buy_list.db"
        self.db_name_setting(db_name, daily_craw_db_name, daily_buy_list_db_name)
        # self.dc = daily_crawler(self.jackbot_db_name, self.daily_craw_db_name, self.daily_buy_list_db_name)

        self.engine_daily_craw = create_engine(
            "mysql+mysqldb://" + cf.db_id + ":" + cf.db_passwd + "@" + cf.db_ip + ":" +cf.db_port+ "/daily_craw",
            encoding='utf-8')
        self.engine_daily_buy_list = create_engine(
            "mysql+mysqldb://" + cf.db_id + ":" + cf.db_passwd + "@" + cf.db_ip + ":" +cf.db_port+ "/daily_buy_list",
            encoding='utf-8')

    def db_name_setting(self,db_name, daily_craw_db_name, daily_buy_list_db_name):

        # 자동으로 실행 위치의 path를 잡아줌
        user = getpass.getuser()
        path = "/Users/"+user+"/Documents/jackbot_v2"
        # print(os.path.realpath(__file__))  # 파일
        # print(os.path.dirname(os.path.realpath(__file__)))  # 파일이 위치한 디렉토리

        # self.simul_jackbot_db_name = path + "/db/" + db_name
        print(sys.platform)

        if sys.platform == 'linux':
            self.jackbot_db_name = '/home/jake/jackbot_v2' + "/db/" + db_name
            self.daily_craw_db_name = '/home/jake/jackbot_v2' + "/db/" + daily_craw_db_name
            self.daily_buy_list_db_name = '/home/jake/jackbot_v2' + "/db/" + daily_buy_list_db_name
        elif sys.platform == 'darwin':
            self.jackbot_db_name = path + "/db/" + db_name
            self.daily_craw_db_name = path + "/db/" + daily_craw_db_name
            self.daily_buy_list_db_name = path + "/db/" + daily_buy_list_db_name

        # self.jackbot_db_name = path + "/db/" + db_name

        # self.craw_db_name = path + "/db/craw.db"
        # self.daily_possessed_item_db = path + "/db/daily_possessed_item.db"
        # self.daily_today_buy_list_db_name = path + "/db/daily_today_buy_list.db"

        # print(self.simul_jackbot_db_name)
        # self.simul_jackbot_db_con = sqlite3.connect(self.simul_jackbot_db_name)
        # self.simul_jackbot_db_cur = self.simul_jackbot_db_con.cursor()
        # self.jackbot_db_con= sqlite3.connect(self.jackbot_db_name)
        # self.jackbot_db_cur=self.jackbot_db_con.cursor()


        self.engine_daily_craw = create_engine("mysql+mysqldb://jake:" + "web22dev##" + "@192.168.0.117/daily_craw", encoding='utf-8')
        self.engine_daily_buy_list = create_engine("mysql+mysqldb://jake:" + "web22dev##" + "@192.168.0.117/daily_buy_list", encoding='utf-8')

        # self.daily_craw_db_con = self.engine.connect()

        # 종목별로 총 일별 데이터 가져오는 db
        # self.daily_craw_db_con = sqlite3.connect(self.daily_craw_db_name)
        #
        # self.daily_craw_db_cur = self.daily_craw_db_con.cursor()

        # self.craw_db_con = sqlite3.connect(self.craw_db_name)
        # self.craw_db_cur = self.craw_db_con.cursor()
        # 일별로 모든 종목들 나열한 db
        # self.daily_buy_list_db_con = sqlite3.connect(self.daily_buy_list_db_name)
        # self.daily_buy_list_db_cur = self.daily_buy_list_db_con.cursor()

    # def code_update_check(self):
    #     # try:
    #
    #     # 유가증권과 코스닥 시장의 종목코드를 가져오는 것은 PyMon이 실행될 때 한 번만 수행되면 되기 때문에 PyMon의 생성자에서 get_code_list 메서드를 호출합니다.
    #
    #     #
    #     # sql = "select daily_buy_list from setting_data where id=1"
    #     # self.jackbot_db_cur.execute(sql)
    #     # # 데이타 Fetch
    #     # # rows 는 list안에 튜플이 있는 [()] 형태로 받아온다
    #     # rows = self.jackbot_db_cur.fetchall()
    #
    #     #
    #     # if rows[0][0] != self.today:
    #     #     self.daily_buy_list_check()
    #     self.daily_buy_list_check()
    #     print("daily_buy_list end!!!!!!!!!!!!!!!!!!!")
    #

    def date_rows_setting(self):
        print("date_rows_setting!!")
        # 날짜 지정
        sql = "select date from `gs글로벌` where date >= '%s' group by date"
        self.date_rows = self.engine_daily_craw.execute(sql % self.start_date).fetchall()

    def is_table_exist_daily_buy_list(self, date):
        sql = "select 1 from information_schema.tables where table_schema ='daily_buy_list' and table_name = '%s'"
        rows = self.engine_daily_buy_list.execute(sql % (date)).fetchall()

        if len(rows) == 1:
            return True
        elif len(rows) == 0:
            return False



    def daily_buy_list(self):
        print("daily_buy_list!!!")
        # date_rows 새로 setting 해야함. 왜냐하면 pymon에서 daily_crawler 돌리고 나서 daily buy list를 가져오기 때문에 daily_crawler 돌리기 전에 init을 통해서
        # self.date_rows를 가져오면 오늘일자에 대한 today_buy_list는 생기지 않는다.
        self.date_rows_setting()
        self.get_stock_item_all()

        for k in range(len(self.date_rows)):
            # print("self.date_rows !!!!", self.date_rows)
            print(str(k)+" 번째 : " + datetime.datetime.today().strftime(" ******* %H : %M : %S *******"))
            # daily 테이블 존재하는지 확인
            if self.is_table_exist_daily_buy_list(self.date_rows[k][0]) == True:
                # continue
                print(self.date_rows[k][0]+ "테이블은 존재한다 !! continue!! ")
                continue
            else:
                print(self.date_rows[k][0] + "테이블은 존재하지 않는다 !!!!!!!!!!! table create !! ")

                multi_list = list()
                # con = sqlite3.connect(self.daily_craw_db_name)
                # cur = con.cursor()
                # print("len!!!!!")
                # print(len(self.stock_item_all))
                for i in range(len(self.stock_item_all)):
                    # # 존재하는지 부터 확인
                    #                     # sql = "SELECT COUNT(*) FROM sqlite_master WHERE Name = ?"
                    #                     # cur.execute(sql, (self.df_stock_all.loc[i, 'code_name']))
                    #                     # rows = cur.fetchall()



                    if self.is_table_exist_daily_craw(self.stock_item_all[i][1],self.stock_item_all[i][0]) == False:
                        print(self.stock_item_all[i][1] + "테이블이 존재하지 않는다 !!")
                        continue

                    sql = "select * from `" + self.stock_item_all[i][0] + "` where date = '%s' group by date"
                    # daily_craw에서 해당 날짜의 row를 한 줄 가져오는 것
                    rows = self.engine_daily_craw.execute(sql % (self.date_rows[k][0])).fetchall()
                    # if len(rows)==0:
                        # print("rows 0이다!!! "+self.stock_item_all[i][0])
                    multi_list+=rows
                # print(multi_list)
                # print(len(multi_list))
                if len(multi_list)!=0:

                    df_temp = DataFrame(multi_list, columns=['index','date', 'check_item', 'code', 'code_name', 'd1_diff_rate','close',  'open', 'high', 'low',
                                                     'volume', 'clo5', 'clo10', 'clo20', 'clo40', 'clo60', 'clo80',
                                                     'clo100', 'clo120', "clo5_diff_rate", "clo10_diff_rate",
                                                     "clo20_diff_rate", "clo40_diff_rate", "clo60_diff_rate",
                                                     "clo80_diff_rate", "clo100_diff_rate", "clo120_diff_rate",
                                                     'yes_clo5', 'yes_clo10', 'yes_clo20', 'yes_clo40', 'yes_clo60', 'yes_clo80',
                                                     'yes_clo100', 'yes_clo120',
                                                     'vol5', 'vol10', 'vol20', 'vol40', 'vol60', 'vol80',
                                                     'vol100', 'vol120'
                                                      ])


                    df_temp.to_sql(name=self.date_rows[k][0], con=self.engine_daily_buy_list, if_exists='replace')

    # def daily_buy_list_check(self):
    #     self.daily_buy_list()
    #
    #     print("daily_buy_list success !!!")

        #
        # sql = "UPDATE setting_data SET daily_buy_list=? WHERE id=?"
        # self.jackbot_db_cur.execute(sql, (self.today, 1))
        # self.jackbot_db_con.commit()


    def get_stock_item_all(self):
        print("get_stock_item_all!!!!!!")
        sql = "select code_name,code from stock_item_all"
        self.stock_item_all=self.engine_daily_buy_list.execute(sql).fetchall()


    # # 안쓰는거 open_api있는데 노신경
    # def daily_crawler_check(self):
    #     # self.dc.cc.daily_db_create()
    #     # self.dc.crawling_data()
    #     self.db_to_daily_craw()
    #
    #     print("daily_crawler success !!!")
    #
    #
    #     sql = "UPDATE setting_data SET daily_crawler=? WHERE id=?"
    #     self.engine_JB.execute(sql, (self.open_api.today, 1))
    #     self.open_api.jackbot_db_con.commit()
    #


        # PyMon의 생성자에서 open_api 클래스의 인스턴스를 생성했고, 이를 self.open_api이 바인딩하고 있습니다.
            # 따라서 self.open_api을 통해 get_code_list_by_market 메서드를 호출함으로써 유가증권시장과 코스닥시장의 종목코드 리스트를 가져올 수 있습니다. 가져온 종목코드 리스트는 get_code_list 메서드뿐 아니라 다른 메서드에서 사용될 것이므로 self.kospi_codes와 self.kosdaq_codes라는 이름으로 각각 바인딩합니다.
    # "stock all vesrsion "







    def is_table_exist_daily_craw(self,code,code_name):
        sql = "select 1 from information_schema.tables where table_schema ='daily_craw' and table_name = '%s'"
        rows = self.engine_daily_craw.execute(sql % (code_name)).fetchall()

        if len(rows)== 1:
            # print(code + " " + code_name + " 테이블 존재한다!!!")
            return True
        elif len(rows) == 0:
            # print("####################" + code + " " + code_name + " no such table!!!")
            # self.create_new_table(self.cc.code_df.iloc[i][0])
            return False





    # 이건 안쓰는거
    # def db_to_today_buy_list(self):
    #     # try:
    #         print("db_to_today_buy_list!!!")
    #
    #
    #         # 여기에 mesu_list 의 """"오늘날짜""""에 있는 종목들을 제외한 놈들을 추려야한다.
    #         # date가 오늘이고, volume(판매량)이 open_api.volume_limit 이상이고 close(종가) 가 invest_unit 보다 작은놈(그래야 살수있다) 그리고 판매량이 높은 순으로 정렬
    #         # db 설계할 때 int, text 구분잘해야한다. 안그러면 원하는 결과가 안나옴.
    #         # group by code 해야 혹시나 겹치는거 있으면 빼고 넣는다. (pymon할때 중복될수도 있음 테스트한다고 check 지웠다가 다시 실행하는 경우)
    #         # not in 보다 not exist가 더빠르다.
    #
    #
    #
    #         # 0226 기존에 today_buy_list 가져오는 방식
    #         # sql = "SELECT * FROM buy_list b WHERE b.volume > ? and b.date = ? and b.close < ? and b.close < b.avg_close * ? and NOT exists (SELECT null FROM possessed_item p where b.code = p.code) group by code order by volume desc"
    #         # avg_close , close 차이로 order by 하는 방식
    #         sql = "SELECT * FROM buy_list b WHERE b.volume > ? and b.date = ? and b.close < ? and b.close < b.avg_close * ? " \
    #               "and NOT exists (SELECT null FROM possessed_item p where b.code = p.code) " \
    #               "and b.code NOT in (select code from stock_konex)" \
    #               "and b.code NOT in (select code from stock_managing)"\
    #               "and b.code NOT in (select code from stock_insincerity)" \
    #               "group by code order by close_avg_diff_rate"
    #
    #         # 무조건 튜플 형태로 실행해야한다. 따라서 인자 하나를 보내더라도 ( , ) 안에 하나 넣어서 보낸다.
    #         # self.engine_JB.execute(sql, (self.open_api.today,))
    #
    #         self.engine_JB.execute(sql, (self.open_api.volume_limit, self.open_api.today, self.open_api.invest_unit, self.open_api.avg_close_multiply_rate))
    #
    #         # 저날 못하면 아래처럼 특정 날짜로
    #         # self.engine_JB.execute(sql, (self.open_api.volume_limit, '20190412', self.open_api.invest_unit, self.open_api.avg_close_multiply_rate))
    #         # 데이타 Fetch
    #         # rows 는 list안에 튜플이 있는 [()] 형태로 받아온다
    #         rows = self.engine_JB.fetchall()
    #
    #
    #         # df_temp = {'id': [], 'code': [], 'date': [], 'open': [],'high': [],'low': [],'close': [],'volume': [],'d1_close': []}
    #         # print(rows)
    #
    #
    #         # 이 때 rows에 없는 컬럼을 추가하면?? 에러 뜬다
    #         df = DataFrame(rows, columns=['id', 'check_item', 'code', 'date', 'open','high','low','close','volume', 'd1_close', 'avg_close','close_avg_diff_rate'])
    #
    #         # df = DataFrame(rows)
    #         # replace로 한다
    #         #  이렇게 저장하면 자동으로 index가 자동증가로 생성되어있다. 왜냐하면 리스트는 기본적으로 인덱스 값을 가지고 있기 때문이다. 일단 이렇게 쓰고 나중에 다듬자.
    #         df.to_sql('today_buy_list', self.open_api.jackbot_db_con, if_exists='replace')
    #                             # ,
    #                             # dtype={
    #                             # 'id':sqlalchemy.types.INTEGER(),
    #                             # 'check_item':sqlalchemy.types.INTEGER(),
    #                             # 'code':sqlalchemy.types.Text(),
    #                             # 'date': sqlalchemy.types.Text(),
    #                             # 'open':sqlalchemy.types.INTEGER(),
    #                             # 'high':sqlalchemy.types.INTEGER(),
    #                             # 'low':sqlalchemy.types.INTEGER(),
    #                             # 'close':sqlalchemy.types.INTEGER(),
    #                             # 'volume':sqlalchemy.types.INTEGER(),
    #                             # 'd1_close':sqlalchemy.types.INTEGER()})
    #
    #
    #                              # 'date':
    #                              # 'intfld':  sqlalchemy.types.INTEGER(),
    #                              # 'strfld': sqlalchemy.types.NVARCHAR(length=255)
    #                              # 'floatfld': sqlalchemy.types.Float(precision=3, asdecimal=True)
    #                              # 'booleanfld': sqlalchemy.types.Boolean})
    #         self.open_api.jackbot_db_con.commit()
    #
    #         sql = "UPDATE setting_data SET today_buy_list=? WHERE id=?"
    #         self.engine_JB.execute(sql, (self.open_api.today, 1))
    #         self.open_api.jackbot_db_con.commit()
    #


    def run(self):



        self.transaction_info()

        # print("run end")
        return 0

if __name__ == "__main__":

    # try:
    #     app = QApplication(sys.argv)
        daily_buy_list = daily_buy_list()
        # pymon.run()




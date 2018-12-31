from datetime import datetime
import pandas as pd

class KuberHoliday():
    def __init__(self,year = 2018):
        self.Holidays_df_2018 = None
        self.year = year
        self.prepare_holidays_list()

    def prepare_holidays_list(self):
        Hol_names_2018 = [
            "Republic day",
            "Good Firday",
            "Independence Day",
            "Gandhi Jayanti",
            "Christmas"
        ]
        Hol_dates_2018 = [
            datetime.strptime('26/01/2018', '%d/%m/%Y').date(),
            datetime.strptime('30/03/2018', '%d/%m/%Y').date(),
            datetime.strptime('15/08/2018', '%d/%m/%Y').date(),
            datetime.strptime('02/10/2018', '%d/%m/%Y').date(),
            datetime.strptime('25/12/2017', '%d/%m/%Y').date()
                    ]

        Hol_days_2018 = [
            "Friday",
            "Tuesday",
            "Wednesday",
            "Tuesday",
            "Tuesday"
        ]
        Holidays_df_2018 = pd.DataFrame({
            "Holiday Name": Hol_names_2018,
            "Date": Hol_dates_2018,
            "Day": Hol_days_2018
        })

        Holidays_df_2018["Date"] = pd.to_datetime(Holidays_df_2018["Date"])
        self.Holidays_df_2018 = Holidays_df_2018

    def holidays_2018_mask(self,seriesval):
        bool_flag = True
        for val in self.Holidays_df_2018["Date"]:
            if seriesval == val:
                bool_flag = False
        return bool_flag

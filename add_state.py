import pandas as pd
import requests

event_df = pd.read_csv('event_data.csv', index_col="id")


def get_state(row):
    # split point into array of the lat and long
    geo_arr = row['geo'].replace("POINT(", "").replace(")", "").split(' ')

    # build url with lat and long & request
    url = "https://us-state-api.herokuapp.com/?lat={}&lon={}".format(geo_arr[1], geo_arr[0])
    r = requests.get(url)
    if r.status_code == 200:
        if r.json()["state"] is not None:
            # return the state code
            return r.json()["state"]["postal"]
        else:
            return ""
    else:
        return ""


# lambda function to go through all rows and assign the state
event_df['state'] = event_df.apply(lambda row: get_state(row), axis=1)

# save to csv so don't have to call api again
event_df.to_csv("event_data_new.csv")



import pandas as pd

import sys, os
def resource_path(rel):
    base = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base, rel)

# excel_file  = pd.read_excel(resource_path('raw_data.xlsx'))
excel_file  = pd.read_excel(resource_path('data.xlsx'))

# # Apply the transformation: multiply by 2 and then subtract 10 for economic and social scores
#excel_file['Economic Score'] = (excel_file['Economic Score'] * 2 - 10)
#excel_file['Social Score'] = (excel_file['Social Score'] * 2 - 10) * -1

#excel_file.to_excel('data.xlsx', index=False)
#
# excel_file = pd.read_excel('data.xlsx')
# print(excel_file)

data = {}
for i, j, k in zip(excel_file["Country"], excel_file["Economic Score"], excel_file["Social Score"]):
    data[i] = j, k
# print(data)

countries = [country for country in excel_file["Country"]]
# print(countries)

# -------------------------- EU -------------------------- #

eu = ["austria", "belgium", "bulgaria", "croatia", "cyprus", "czech republic", "denmark", "estonia", "finland",
      "france", "germany", "greece", "hungary", "ireland", "italy", "latvia", "lithuania", "luxembourg", "malta",
      "netherlands", "poland", "portugal", "romania", "slovakia", "slovenia", "spain", "sweden"]

data_eu = {}
for country in eu:
    data_eu[country.title()] = data[country.title()]
# print(data_eu)

# -------------------------- G20 -------------------------- #

g20 = ["argentina", "australia", "brazil", "canada", "china", "france", "germany", "india", "indonesia", "italy",
       "japan", "south korea", "mexico", "russia", "saudi arabia", "south africa", "turkey", "united kingdom",
       "united states"]  # Add "european union" to list (optional)

data_g20 = {}
for country in g20:
    data_g20[country.title()] = data[country.title()]
# print(data_g20)

# -------------------------- NATO -------------------------- #

nato = ["albania", "belgium", "bulgaria", "canada", "croatia", "czech republic", "denmark", "estonia", "finland",
        "france", "germany", "greece", "hungary", "iceland", "italy", "latvia", "lithuania", "luxembourg", "montenegro",
        "netherlands", "north macedonia", "norway", "poland", "portugal", "romania", "slovakia", "slovenia", "spain", "sweden",
        "turkey", "united kingdom", "united states"]


data_nato = {}
for country in nato:
    data_nato[country.title()] = data[country.title()]
# print(data_nato)


# ---------------------- USA STATES ----------------------- #

# data_usa = pd.read_excel(r'usa_state_data.xlsx')
#
# data_usa.rename(columns={"Real Economic Index": "Relative Economic Values",
#                          "Real Social Index": "Relative Social Values"}, inplace=True)
#
# data_usa["Relative Economic Values"] = data_usa["Relative Economic Values"] * 10
# data_usa["Relative Social Values"] = data_usa["Relative Social Values"] * -10
#
# data_usa.insert(3, "Real Economic Values", (data_usa["Relative Economic Values"] + 7.77)/2)
# data_usa.insert(4, "Real Social Values", (data_usa["Relative Social Values"] - 7.10)/2)
#
# data_usa.to_excel("data_usa.xlsx")


excel_file2 = pd.read_excel(resource_path('data_usa.xlsx'))
data_usa_real = {}
data_usa_relative = {}
for i, j, k, l, m in zip(excel_file2["State"], excel_file2["Real Economic Values"], excel_file2["Real Social Values"],
                         excel_file2["Relative Economic Values"], excel_file2["Relative Social Values"]):
    data_usa_real[i] = j, k
    data_usa_relative[i] = l, m
data_usa = {"Real": data_usa_real, "Relative": data_usa_relative}

# print(data_usa["Real"])
# print(data_usa["Relative"])
# print(data_usa)

states = [state for state in excel_file2["State"]]
# print(states)

search_states = [state + " - USA" for state in excel_file2["State"]]
data_search = countries + search_states

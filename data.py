import pandas as pd

# # Get table
# economic_data = pd.read_html('https://en.wikipedia.org/wiki/Index_of_Economic_Freedom#Rankings_and_scores', header=0)[0]
# social_data = pd.read_html('https://en.wikipedia.org/wiki/Democracy_Index#Components', header=0)[6]
# # The 6 indicates what section we require (main table data)

# # Get required columns
# economic_data = economic_data[['Country', 'Score']]
# social_data = social_data[['Country', 'Overall score']]

# # Merging with countries present in the two dataframes only
# data = pd.merge(economic_data, social_data, on=['Country'])

# # Rename the headers
# data.rename(columns={"Score": "Economic Score", "Overall score": "Social Score"}, inplace=True)
# data = data.sort_values("Country")

# # Reset index
# data = data.reset_index(drop=True)  # drop previous index

# # Convert values to numeric
# data = data.astype({"Economic Score": float, "Social Score": float})

# # Save raw data to excel
# # data.to_excel("raw_data.xlsx")

# # Make values between -10 and 10
# data["Economic Score"] = (data["Economic Score"]/10) * 2 - 10   # +0.5 value is bias
# data["Social Score"] = ((data["Social Score"] - 0.75) * 2 - 10) * -1  # -0.75 value is bias
# # print(data)

# # Save adjusted data to excel
# # data.to_excel("data.xlsx")

excel_file = pd.read_excel('data.xlsx')
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

excel_file2 = pd.read_excel('data_usa.xlsx')
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

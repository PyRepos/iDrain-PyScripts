import met_office_api_call
from arcgis.gis import GIS
import json

# API Configuration

KEY = "95de7e4d-246e-408b-aa6f-695a1935fd94"

stations = {
    '3354':'WATNALL',
    '3535':'COLESHILL',
    '3544':'CHURCH LAWFORD',
    '3462':'WITTERING',
    '3379':'CRANWELL',
    '3377':'WADDINGTON'
    }

station_url ={
    'WATNALL':'http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/3354?res=3hourly&key=95de7e4d-246e-408b-aa6f-695a1935fd94',
    'COLESHILL':'http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/3535?res=3hourly&key=95de7e4d-246e-408b-aa6f-695a1935fd94',
    'CHURCH LAWFORD':'http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/3544?res=3hourly&key=95de7e4d-246e-408b-aa6f-695a1935fd94',
    'WITTERING':'http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/3462?res=3hourly&key=95de7e4d-246e-408b-aa6f-695a1935fd94',
    'CRANWELL':'http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/3379?res=3hourly&key=95de7e4d-246e-408b-aa6f-695a1935fd94',
    'WADDINGTON':'http://datapoint.metoffice.gov.uk/public/data/val/wxfcs/all/json/3377?res=3hourly&key=95de7e4d-246e-408b-aa6f-695a1935fd94',
    }

IDRAIN_CONFIG = {
    'AGOUser' : 'CARNELL_DEV1',
    'AGOPwd'  : 'Carnell2018',
    'AGOItem' : '9b8be9d00b5042bf85baed1688198c18'
    }

# Log on and capture data from Met Office
ctor = met_office_api_call.Manager("KEY")

# Download data from the API
dataContainer={}
for key,value in station_url.items(): 
    dataValue = ctor._call_api(value)
    dataValue = json.loads(dataValue)
    #dataValue = ctor._convert_to_dictionary()
    dataContainer.update({key:dataValue})

WeatherReeds = {}
for key, value in dataContainer.items():
    for data in value['SiteRep']['DV']['Location']['Period']:
        for str in data['Rep']:
            condition = []
            condition.append(str['D'])  # Wind Direction
            condition.append(str['S'])  # wind Speedv mile/hour
            condition.append(str['G'])  # Wind Gust mile/hour
            condition.append(str['V'])  # Visibility
            condition.append(str['Pp']) # Precipitation Probability 
            condition.append(str['W'])  # Significant weather 
    WeatherReeds.update({key : condition})

# Parse specific data from file
gis = GIS("https://arcgis.com", IDRAIN_CONFIG['AGOUser'], IDRAIN_CONFIG['AGOPwd'])

# Get WMS from gis item
idrainItem = gis.content.get(IDRAIN_CONFIG['AGOItem'])

# Get weather station layer
featureLayer = idrainItem.layers[2]

# Make a query to the features of the layer with specific id or other attributes
queryResult = featureLayer.query()
edit_features = queryResult.features

# Define temp editing features for updating features
for editfeature in edit_features:
    for key,value in WeatherReeds.items():
        if key in editfeature.attributes['Site_Name']:
            editfeature.attributes['Wind_Direct'] = value[0]
            editfeature.attributes['Wind_Speed'] = value[1]
            editfeature.attributes['Wind_Gust'] = value[2]
            editfeature.attributes['Visibility'] = value[3]
            editfeature.attributes['Pressure'] = value[4]
            editfeature.attributes['Significan'] = value[5]
            update_result = featureLayer.edit_features(updates=[editfeature])
            break

print ("Weather feed is updated")







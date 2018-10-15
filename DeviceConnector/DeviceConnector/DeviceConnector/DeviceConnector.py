from arcgis.gis import GIS
import pyodbc
import logging

# ---------- Configure SQL Server & ArcGIS Online -------- #

IDRAIN_CONFIG = {
    # SQL Server Configuration
    'LOG':'idrain.log',
    'ConnectString' : 'DRIVER={SQL Server};SERVER=CARNELL99\ARC_SQLEXPRESS;DATABASE=iDrain;UID=HaoYe;PWD=Carnell2018',

    # ARCGIS Online Configuration
    'AGOUser' : 'CARNELL_DEV1',
    'AGOPwd'  : 'Carnell2018',
    'AGOItem' : '9b8be9d00b5042bf85baed1688198c18'
}

# ---------- Retrieve updates from SQL Server -------------#

# Configure data bridge
logging.basicConfig(filename=IDRAIN_CONFIG['LOG'])
logging.basicConfig(filemode='w', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

# Processing Monitoring
print ("Connecting SQL Server")
logging.info("Connecting SQL Server")

# Specifying the ODBC driver, server name, database, etc. directly 
cnxn = pyodbc.connect(IDRAIN_CONFIG['ConnectString'])

# Create a cursor from the connection
cursor = cnxn.cursor()

# Create a temporary container for data
UpdatedDataSet = {}

# Processing Monitoring
print ("Reading Data from SQL Server")
logging.info("Reading Data from SQL Server")

# Define a cursor to retrieve the latest data
cursor.execute("select t1.DeviceID,t1.ReadingTypeID, t1.Timestamp from dbo.Readings as t1 INNER JOIN (select DeviceID, max(timestamp) as LatestDate from dbo.Readings group by DeviceID ) as t2 ON t1.Timestamp = t2.LatestDate")

rows = cursor.fetchall()
for row in rows:
    UpdatedDataSet[row.DeviceID] = row.ReadingTypeID

# Block 2 - Update map data to ArcGIS online --------------------- #

# Processing Monitoring
print ("Connecting ArcGIS Online")
logging.info("Connecting ArcGIS Online")

# Get access to AGO
gis = GIS("https://arcgis.com", IDRAIN_CONFIG['AGOUser'], IDRAIN_CONFIG['AGOPwd'])

# Get WMS from gis item
idrainItem = gis.content.get(IDRAIN_CONFIG['AGOItem'])

# Processing Monitoring
print ("Updating ArcGIS Online")
logging.info("Updating ArcGIS Online")

# Get web feature layer from WMS, note that in AGO it must be enabled as a WFS
featureLayer = idrainItem.layers[0]

# Make a query to the features of the layer with specific id or other attributes
queryResult = featureLayer.query()
edit_features = queryResult.features

# Define temp editing features for updating features
for editfeature in edit_features:
    for key in UpdatedDataSet.keys():
        if editfeature.attributes['F_DeviceID'] == key:
            editfeature.attributes['CurrentStatus'] = UpdatedDataSet[key] 
            update_result = featureLayer.edit_features(updates=[editfeature])
            break

# Processing Monitoring
print ("Updating is completed")
logging.info("Updating is completed")
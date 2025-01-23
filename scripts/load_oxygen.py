import random
import openpyxl
from django.contrib.auth import get_user_model
from core.models import *
from django.contrib.auth.models import Group
from decimal import Decimal
import json

# mapshaper reduced-lrs.geojson -simplify dp 10% -o reduced-mapshaper-lrs.geojson
#mapshaper reduced-counties.geojson -simplify dp 10% -o reduced-mapshaper-counties.geojson

modify_counties = {
    "Prince Georges, MD": "Prince George's, MD",
    "Baltimore City, MD": "Baltimore, MD",
    "Charlottesville City, VA": "Charlottesville, VA",
    "Chesapeake City, VA": "Chesapeake, VA",
    "Colonial Heights City, VA": "Colonial Heights, VA",
    "Fairfax City, VA": "Fairfax, VA",
    "Falls Church City, VA": "Falls Church, VA",
    "Fredericksburg City, VA": "Fredericksburg, VA",
    "Hampton City, VA": "Hampton, VA",
    "Harrisonburg City, VA": "Harrisonburg, VA",
    "Hopewell City, VA": "Hopewell, VA",
    "Manassas City, VA": "Manassas, VA",
    "Manassas Park City, VA": "Manassas Park, VA",
    "Newport News City, VA": "Newport News, VA",
    "Norfolk City, VA": "Norfolk, VA",
    "Petersburg City, VA": "Petersburg, VA",
    "Poquoson City, VA": "Poquoson, VA",
    "Portsmouth City, VA": "Portsmouth, VA",
    "Richmond City, VA": "Richmond, VA",
    "Virginia Beach City, VA": "Virginia Beach, VA",
    "Winchester City, VA": "Winchester, VA",
    "Covington City, VA": "Covington, VA",
    "Lexington City, VA": "Lexington, VA",
    "Lynchburg City, VA": "Lynchburg, VA",
    "Staunton City, VA": "Staunton, VA",
    "Waynesboro City, VA": "Waynesboro, VA",
    "Williamsburg City, VA": "Williamsburg, VA",
    "Mckean, PA": "McKean, PA",
    "Queen Annes, MD": "Queen Anne's, MD",
    "St. Marys, MD": "St. Mary's, MD",
    "Isle Of Wight, VA": "Isle of Wight, VA",
    "King And Queen, VA": "King and Queen, VA",
    "Suffolk City, VA": "Suffolk, VA"
}
modify_counties_inv = {value: key for key, value in modify_counties.items()}

states_dict = {'DE': '10', 'DC': '11', 'MD': '24', 'NY': '36', 'PA': '42', 'VA': '51', 'WV': '54'}

states_inv_dict= {value: key for key, value in states_dict.items()}
def load_oxygen_data():

    filename = 'scripts/data.xlsx'

    xlsx = openpyxl.load_workbook(filename)
    sheet_names = xlsx.get_sheet_names()

    print (sheet_names)
    filename = 'static/reduced-mapshaper-lrs.geojson'
    geographies = GeographicArea.objects.all()
    current_geographies = []

    for geography in geographies:
        current_geographies.append(f'{geography.name}, {geography.state}')

    with open(filename, 'r') as f:
        data = json.load(f)
        for feature in data['features']:
            lrseg_name = feature['properties']['LndRvrSeg']
            if (LandRiverSegment.objects.filter(name=lrseg_name).count() > 0):
                lrseg = LandRiverSegment.objects.get(name=lrseg_name)
                fips = feature['properties']['FIPS']
                state = (lrseg.state.abbreviation).upper()
                county = lrseg.geographic_area.name
                acres = feature['properties']['Acres'],
                new_feature = {
                        "type": feature['type'],
                        "geometry": feature['geometry'],
                        "properties": {
                            "Id": lrseg.id,
                            "CountyId": lrseg.geographic_area.id, 
                            "GeographyType": "lrs",
                            "LndRvrSeg": lrseg_name,
                            "FIPS": fips,
                            "State": state,
                            "County": county,
                            "Acres": acres
                        }
                    }
                lrseg.geo_data=new_feature
                lrseg.save()

def run():
    lrs()

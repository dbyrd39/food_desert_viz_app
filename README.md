# North Carolina Food Environment Map: Streamlit + Folium

This application builds an interactive map of **North Carolina** showing:
- **Food deserts**
- **Food swamps**
- **Healthy outlets**
- **Unhealthy outlets**
- **County boundaries**
- **Population-weighted deserts/swamps**
- **Nutrition layer** (in progress)

## Objective

The goal of this project is to identify food environments in North Carolina that:
- Lack reliable food access (indicating the presence of a food desert)
- Have reliable food access but lack healthy food access (indicating the presence of a food swamp)

## Methodology 

Food deserts are geographic locations that lack reliable food access. The USDA identifies multiple Low Income-Low Access conditions. A census tract is considered a food desert if it is low income (poverty rate >= 20% OR median family income <= 80% of state median/area median) and low access (urban tracts where >=500 people or >=33% of residents live more than 1 mile from a supermarket, or rural tracts where the same amount of people live more than 10 miles from a supermarket). This application calculates the number of USDA food-access indicators present within a census tract and assigns a score based on how many indicators are present. For example, a score of 3 means that there are 3 food desert indicators present. Future versions of this project will take into account vehicle access and senior-specific measures.

Similarly, food swamps are geographic locations that specifically lack healthy food access. Food swamps do not have an official USDA classification, but it is usually considered to be a location where unhealthy food options greatly outnumber healthy food options. There is readily available food access, but it is not nutritionally sufficient for a population. In the context of this project, grocery stores and supermarkets are considered healthy food sources, while fast food establishments are considered unhealthy food sources. For this application, the food swamp index for a particular census tract is: 

unhealthy outlets / (healthy outlets + 1)

Note: The +1 ensures that the denominator is never 0.

Population-weighted food deserts/swamps are incorporated as additional layers. These layers are similar to the unweighted layers, except they use a population-weighted score to determine presence and severity of food deserts and swamps. The current scoring algorithm is simply the severity (or index) multiplied by the population of the census tract. Theoretically, these layers allow users to identify which census tracts contain the largest numbers of people suffering from the worst food environment conditions. Although the score itself has little mathematically meaning beyond "higher score = worse", the value allows the opacity-scaling of the application to depict the most problematic areas in terms of number of people impacted. 

Future versions of this project will implement an additional nutrition layer that analyzes the actual inventory of healthy food outlets to determine how nutritious they actually are. Even though a supermarket or a grocery store is present in a census tract, it may lack healthy food options compared to grocery stores in other census tracts. This additional nutrition layer will allow users to inspect locations that are considered "healthy" sources by the USDA and determine if they are actually meeting the needs of the population.

## Data

- Census tracts/county lines are fetched from US Census TIGER/Line.
- Food deserts are computed from a USDA Food Access Research Atlas CSV (you provide the CSV in `data/raw/cache/usda_food_access.csv` or pass a URL in the build script).
- Food swamps are computed from OSM outlet counts.
- Nutrition scores are still in progress

This application makes use of cached directories when possible, improving speed and performance. Additionally, data is totally ingested prior to loading the map, so re-calculations do not occur when layers are toggled on and off. Streamlit does have to buffer, but having data ingestion totally occur on the front end prevents Streamlit from crashing. As a result, this application prioritizes consistency and functionality over real-time analysis. Higher-powered resources and access to expensive data warehouses would allow this application to function in real-time. 

## Visualization

The interactive map consists of the layers mentioned at the beginning of this document. Users can toggle different layers on and off to see each analysis in isolation or see how different layers interact.

Census tract food deserts and food swamps are illustrated as shaded polygons, where the opacity of the polygon is correlated with the food desert severity (number of UDSA indicators present) or food swamp index (see formula above), depending on which layer is currently present. Healthy and unhealthy outlets are depicted as points (green points indicate a healthy option, orange points indicate an unhealthy option). Tooltips exist for polygons and points; desert/swamp polygon tooltips contain tract number, population, and severity/index, and outlet point tooltips contain the outlet name and the type (healthy vs. unhealthy).

Population-weighted food deserts and food swamps work similarly to the non-weighted layers, except they calculate a population-weighted score (severity * population OR index * population). The population-weighted tooltips contain tract number and population-weighted score. 

County boundaries can be toggled on and off to inspect food environments on a broader county-level rather than a narrow tract-level. 


## Insights

Based on the application's analysis, large cities tend to have food deserts and swamps with the worst population-weighted scores. Charlotte and Raleigh in particular have several tracts with weighted desert scores in the mid 20,000's. Census tract 37025041202 near Charlotte has a pop-weighted swamp impact of 76428. 

Food swamps are much more prevalant than food deserts. Based on a visual inspection alone, only 1-2% of census tracts in NC are a type of food desert. A targeted solution can be implemented to provide these populations with food access. Food swamps appear to cover more than half of the state. This points to a larger societal issue, where unhealthy food access has unfortunately become an acceptable living standard. The solution here will be much more sophisticated. The next version of this project will include a simple script that returns an organized list of tracts based on severity of food conditions, so that users can corroborate their visual analysis with a numerical analysis. 


## Setup
```bash
python -m venv .venv
source .venv/bin/activate           # mac/linux
# .venv\Scripts\activate          # windows

pip install -r requirements.txt
```

## Build 
Run once (or whenever you want to refresh data):
```bash
python scripts/build_nc_layers.py
```

## Run
```bash
streamlit run app/main.py
```

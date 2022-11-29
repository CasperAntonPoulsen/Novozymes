import plotly.express as px
import plotly.graph_objects as go

import datashader as ds
from pyproj import Transformer
from colorcet import fire
import datashader.transfer_functions as tf
from data import EarthquakeData

class EarthquakeVisuals:
    def __init__(self, timeDelta=10, region="us"):
        self.dataLoader= EarthquakeData("earthquakes_decade.json")
        self.df = self.dataLoader.loadData(deltaYears=timeDelta, region=region)
        self.region = region


    def logPlot(self):
        magnitude_count = self.df[self.df["magnitude"] >0]["magnitude"].round(1).value_counts().reset_index()
        magnitude_count.columns = ["magnitude", "count"]

        fig = px.scatter(magnitude_count, x="magnitude", y= "count", log_y=True, template="plotly_dark")

        return fig


    def scatterMap(self):
        #   Scatter map of earthquakes on the continental US
        #   
        #   Renders an image containing the scatter information layers in on top of a map. 
        #   This limits the amount of interaction you can have with the plots, 
        #   but it allows for millions of data points to be included in the visual.

        if self.region == "europe":
            zoom = 2.4
        else:
            zoom = 2.9

        #   Render the image of the scatter information
        #   
        #   The coordinates from the Comcat catalog uses WGS 84 aka EPSG 4326 as coordinate reference system (CRS)
        #   The CRS used by online maps like google maps and open street map, and therefor also plotly is EPSG 3857
        #   
        #   Before rendering the raster data the coordinates need to be saved so the scatter data isnt distorted
        t3857_to_4326 = Transformer.from_crs(3857, 4326, always_xy=True)

        self.df.loc[:, "longitude_3857"], self.df.loc[:, "latitude_3857"] = ds.utils.lnglat_to_meters(
            self.df.longitude, self.df.latitude
        )

        #   Rendering the image
        RESOLUTION = 1000
        cvs = ds.Canvas(plot_width=RESOLUTION, plot_height=RESOLUTION)
        agg = cvs.points(self.df, x="longitude_3857", y="latitude_3857")
        img = tf.shade(agg, cmap=fire).to_pil()
        
    
        #   Coordinates matching the edges of the view as well as the center
        coordinates =[t3857_to_4326.transform(
                        agg.coords["longitude_3857"].values[a],
                        agg.coords["latitude_3857"].values[b],
                    )
                    for a, b in [(0, -1), (-1, -1), (-1, 0), (0, 0)]]
        center_x = coordinates[0][0] + (coordinates[1][0] - coordinates[0][0])/2
        center_y = coordinates[0][1] + (coordinates[-1][1] - coordinates[0][1])/2
        
        #   Create the figure
        fig = go.Figure(go.Scattermapbox())
        fig.update_layout(
            mapbox={
                # View and style information
                "style": "carto-darkmatter",
                "center": go.layout.mapbox.Center(
                            lon=center_x,
                            lat=center_y
                        ),
                "zoom":zoom,

                # Layer the image on top of the map, matching the correct coords
                # to avoid the data being distorted
                "layers": [
                    {
                        "sourcetype": "image",
                        "source": img,
                        "coordinates": coordinates
                    }
                ],
            },
            margin={"l": 0, "r": 0, "t": 0, "b":0},
        )
        
        return fig
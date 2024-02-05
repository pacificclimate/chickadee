import os
import shapely.geometry
import numpy as np
from birdy import WPSClient
from netCDF4 import Dataset
from datetime import datetime
from requests_html import HTMLSession
from ipywidgets import *
from ipyleaflet import *
from IPython import display as ipydisplay

# Instantiate the clients to the two birds. This instantiation also takes advantage of asynchronous execution by setting `progress` to True.
chickadee_url = "http://docker-dev03.pcic.uvic.ca:30102"
chickadee = WPSClient(chickadee_url, progress=True)
finch_url = "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/finch/wps"
finch = WPSClient(finch_url, progress=True)

# These outputs store the WPS responses to track the bird processes
chickadee_output = None
finch_output = None

sub_layers = LayerGroup()
thredds_base = (
    "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/dodsC/datasets"
)
thredds_catalog = (
    "https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/catalog/datasets"
)


def in_bc(point):
    bc = f"{thredds_base}/storage/data/climate/PRISM/dataportal/pr_monClim_PRISM_historical_run1_197101-200012.nc"
    bc_data = Dataset(bc)
    bc_lat = bc_data.variables["lat"][:]
    bc_lon = bc_data.variables["lon"][:]
    # Check if center point is within lat/lon grid
    if (
        (point[0] < bc_lat[0])
        or (point[0] > bc_lat[-1])
        or (point[1] < bc_lon[0])
        or (point[1] > bc_lon[-1])
    ):
        return False
    # Check if center point is closest to a masked data value
    else:
        lat_index = np.argmin(np.abs(bc_lat - point[0]))
        lon_index = np.argmin(np.abs(bc_lon - point[1]))
        pr = bc_data.variables["pr"][0, lat_index, lon_index]
        if pr.mask:
            return False
    return True


def get_subdomain(lat_min, lat_max, lon_min, lon_max, color, name):
    coords = [(lat_min, lon_min), (lat_max, lon_max)]
    return Rectangle(bounds=coords, color=color, name=name, draggable=True)


def get_models():
    session = HTMLSession()
    r = session.get(
        f"{thredds_catalog}/storage/data/climate/downscale/BCCAQ2/CMIP6_BCCAQv2/catalog.html"
    )
    models = []
    exclude = [
        "CMIP6_BCCAQv2",
        "CWEC2020_Factors/",
        "Degree_Climatologies/",
        "Ensemble_Averages/",
        "nobackup/",
        "--",
        "",
    ]
    for tt in r.html.find("tt"):
        if tt.text not in exclude:
            models.append(tt.text[:-1])
    models.sort()
    return models


def handle_dataset_change(change):
    technique.disabled = not technique.disabled
    model.disabled = not model.disabled
    scenario.disabled = not scenario.disabled


def handle_model_change(change):
    if model.value == "CanESM5":
        canesm5_run.disabled = False
    else:
        canesm5_run.disabled = True


def handle_interact(**kwargs):
    point = (
        round(kwargs.get("coordinates")[0], 5),
        round(kwargs.get("coordinates")[1], 5),
    )
    center_hover.value = str(point)
    if kwargs.get("type") == "click":
        # Check if point is within PRISM region
        if not in_bc(point):
            return
        # Remove previous center point and subdomains
        for layer in sub_layers.layers:
            sub_layers.remove_layer(layer)

        # Add new subdomains
        m.center_point = point
        center.value = str(m.center_point)
        center_marker = Marker(location=m.center_point, name="Marker")

        m.lat_min_obs, m.lat_max_obs = (
            m.center_point[0] - 1.25,
            m.center_point[0] + 1.25,
        )
        m.lon_min_obs, m.lon_max_obs = (
            m.center_point[1] - 1.25,
            m.center_point[1] + 1.25,
        )
        m.lat_min_gcm, m.lat_max_gcm = (
            m.center_point[0] - 1.5,
            m.center_point[0] + 1.5,
        )
        m.lon_min_gcm, m.lon_max_gcm = (
            m.center_point[1] - 1.5,
            m.center_point[1] + 1.5,
        )

        gcm_subdomain = get_subdomain(
            m.lat_min_gcm, m.lat_max_gcm, m.lon_min_gcm, m.lon_max_gcm, "blue", "GCM"
        )
        obs_subdomain = get_subdomain(
            m.lat_min_obs, m.lat_max_obs, m.lon_min_obs, m.lon_max_obs, "red", "Obs"
        )

        sub_layers.add_layer(center_marker)
        sub_layers.add_layer(gcm_subdomain)
        sub_layers.add_layer(obs_subdomain)
        m.add_layer(sub_layers)


output_widget = Output()  # Used to print bird progress to main workflow


@output_widget.capture()
def handle_run_chickadee(arg):
    # Obtain the input data files from the THREDDS data server (https://docker-dev03.pcic.uvic.ca/twitcher/ows/proxy/thredds/catalog.html)
    data_vars = {"pr": "pr", "tasmax": "tmax", "tasmin": "tmin"}

    gcm_var = clim_vars.value
    obs_var = data_vars[gcm_var]

    if dataset.value == "PNWNAmet":
        gcm_file = f"{thredds_base}/storage/data/projects/dataportal/data/vic-gen2-forcing/PNWNAmet_{gcm_var}_invert_lat.nc"
    else:
        if technique.value == "BCCAQv2":
            technique_dir = "BCCAQ2"
            model_dir = model.value
        else:
            technique_dir = "MBCn"
            model_dir = model.value + "_10"
        model_catalog = f"{thredds_catalog}/storage/data/climate/downscale/{technique_dir}/CMIP6_{technique.value}/{model_dir}/catalog.html"

        session = HTMLSession()
        r = session.get(model_catalog)
        for tt in r.html.find("tt"):
            file = tt.text
            if (gcm_var in file) and (scenario.value in file):
                if (model.value == "CanESM5") and (canesm5_run.value not in file):
                    continue
                break
        gcm_file = f"{thredds_base}/storage/data/climate/downscale/{technique_dir}/CMIP6_{technique.value}/{model_dir}/{file}"

    obs_file = f"{thredds_base}/storage/data/climate/PRISM/dataportal/{obs_var}_monClim_PRISM_historical_run1_{period.value}.nc"
    gcm_dataset = Dataset(gcm_file)
    obs_dataset = Dataset(obs_file)

    # Obtain the datasets' latitudes and longitudes to determine the subdomains
    gcm_lats = gcm_dataset.variables["lat"][:]
    gcm_lons = gcm_dataset.variables["lon"][:]
    obs_lats = obs_dataset.variables["lat"][:]
    obs_lons = obs_dataset.variables["lon"][:]
    gcm_lat_indices = get_index_range(gcm_lats, m.lat_min_gcm, m.lat_max_gcm)
    gcm_lon_indices = get_index_range(gcm_lons, m.lon_min_gcm, m.lon_max_gcm)
    obs_lat_indices = get_index_range(obs_lats, m.lat_min_obs, m.lat_max_obs)
    obs_lon_indices = get_index_range(obs_lons, m.lon_min_obs, m.lon_max_obs)
    gcm_lat_range = f"[{gcm_lat_indices[0]}:{gcm_lat_indices[1]}]"
    gcm_lon_range = f"[{gcm_lon_indices[0]}:{gcm_lon_indices[1]}]"
    obs_lat_range = f"[{obs_lat_indices[0]}:{obs_lat_indices[1]}]"
    obs_lon_range = f"[{obs_lon_indices[0]}:{obs_lon_indices[1]}]"

    # Use full time range of each dataset
    gcm_ntime = len(gcm_dataset.variables["time"][:])
    gcm_time_range = f"[0:{gcm_ntime - 1}]"
    obs_ntime = len(obs_dataset.variables["time"][:])
    obs_time_range = f"[0:{obs_ntime - 1}]"
    gcm_dataset.close()
    obs_dataset.close()

    # Request a subset of each dataset based on the array indices for each subdomain
    gcm_subset_file = f"{gcm_file}?time,lat{gcm_lat_range},lon{gcm_lon_range},{gcm_var}{gcm_time_range}{gcm_lat_range}{gcm_lon_range}"
    obs_subset_file = f"{obs_file}?time,lat{obs_lat_range},lon{obs_lon_range},climatology_bounds,crs,{obs_var}{obs_time_range}{obs_lat_range}{obs_lon_range}"

    # Put together the parameters for `chickadee.ci`.
    # In the case for `pr`, the `units_bool` parameter is set to `False` in order to avoid converting the PRISM's `mm` units to the PNWNAmet's `mm/day` units.
    (start_date, end_date) = period.value.split("-")
    start_date = datetime.strptime(start_date, "%Y%m")
    end_date = datetime.strptime(end_date + "31", "%Y%m%d")
    chickadee_params = {
        "gcm_file": gcm_subset_file,
        "obs_file": obs_subset_file,
        "gcm_varname": gcm_var,
        "obs_varname": obs_var,
        "max_gb": 0.5,
        "start_date": start_date,
        "end_date": end_date,
    }
    if gcm_var == "pr":
        chickadee_params["units_bool"] = False
        chickadee_params["pr_units"] = "mm/day"
    if dataset.value == "PNWNAmet":
        chickadee_params[
            "out_file"
        ] = f"{gcm_var}_{dataset.value}_target_{period.value}_on-demand.nc"
    else:
        if not canesm5_run.disabled:
            chickadee_params[
                "out_file"
            ] = f"{gcm_var}_{dataset.value}_{technique.value}_{model.value}_{canesm5_run.value}_{scenario.value}_target_{period.value}_on-demand.nc"
        else:
            chickadee_params[
                "out_file"
            ] = f"{gcm_var}_{dataset.value}_{technique.value}_{model.value}_{scenario.value}_target_{period.value}_on-demand.nc"

    print("Running Chickadee")
    global chickadee_output
    chickadee_output = chickadee.ci(**chickadee_params)


@output_widget.capture()
def handle_run_finch(arg):
    if chickadee_output is None or chickadee_output.isNotComplete():
        print(
            "Chickadee process has not completed. Cannot run Finch without the Chickadee output."
        )
        return

    # Get THREDDS location of large Chickadee output to pass to Finch
    chickadee_output_url = chickadee_output.get()[0]
    chickadee_output_thredds = thredds_base + "birdhouse_wps_outputs/"
    chickadee_output_thredds += chickadee_output_url.split("wpsoutputs/")[1]

    # Get climate index corresponding to climate variable in Chickadee output
    with Dataset(chickadee_output_thredds) as dset:
        if "pr" in dset.variables:
            process = finch.wetdays
            kwargs = {"thresh": "10 mm/day", "output_name": "r10mm"}
        elif "tasmin" in dset.variables:
            process = finch.tn_min
            kwargs = {"output_name": "tn_min_ys"}
        else:
            process = finch.tx_max
            kwargs = {"output_name": "tx_max_ys"}

    print("Running Finch")
    global finch_output
    finch_output = process(chickadee_output_thredds, **kwargs)


def get_index_range(arr, min_val, max_val):
    """Compute the indices in an array that correspond to the array's values
    closest to desired min/max values."""
    min_index = np.argmin(np.abs(arr - min_val))
    max_index = np.argmin(np.abs(arr - max_val))
    return (min_index, max_index)


def get_bird_output(resp):
    """Get the URL of the Chickaee/Finch output file for downloading."""
    if resp.isNotComplete():
        print("Bird process is not complete.")
    else:
        print("Process status: " + resp.status)
        print("Link to process output: " + resp.get()[0])


def bird_output_to_dataset(resp):
    """Open Chickadee/Finch output via its THREDDS location using netCDF4.Dataset for further examination."""
    url = resp.get()[0]
    thredds_url = thredds_base + "birdhouse_wps_outputs/" + url.split("wpsoutputs")[1]
    ds = Dataset(thredds_url)
    return ds


# Initialize interactive map and associated widgets
mapnik = basemap_to_tiles(basemaps.OpenStreetMap.Mapnik)
mapnik.base = True
mapnik.name = "Default"

m = Map(
    basemap=mapnik,
    center=(53.5, -120),
    zoom=5,
    layout=Layout(height="600px"),
)
m.on_interaction(handle_interact)
m.center_point = ()

legend = LegendControl(
    {"GCM": "blue", "Obs": "red"}, name="Subdomains", position="topright"
)
m.add_control(legend)

center_hover = Text(value="", placeholder="")
center = Text(value="", placeholder="", description="Center:")
clim_vars = RadioButtons(
    options=["pr", "tasmax", "tasmin"], description="Climate variable:"
)
dataset = RadioButtons(options=["PNWNAmet", "CMIP6"], description="Dataset:")
dataset.observe(handle_dataset_change)

technique = RadioButtons(
    options=["BCCAQv2", "MBCn"],
    description="CMIP6 downscaling technique:",
    disabled=True,
)
model = Dropdown(options=get_models(), description="CMIP6 model:", disabled=True)
model.style.description_width = "100px"
model.observe(handle_model_change)

canesm5_runs = ["r" + str(r) + "i1p2f1" for r in range(1, 11)]
canesm5_run = Dropdown(options=canesm5_runs, description="CanESM5 run:", disabled=True)
canesm5_run.style.description_width = "100px"

scenario = RadioButtons(
    options=[("SSP1-2.6", "ssp126"), ("SSP2-4.5", "ssp245"), ("SSP5-8.5", "ssp585")],
    description="CMIP6 emissions scenario:",
    disabled=True,
)
period = RadioButtons(
    options=["197101-200012", "198101-201012"], description="Climatological period:"
)

run_chickadee = Button(
    description="Run Chickadee",
    button_style="success",
    disabled=False,
    tooltip="Click 'Run' to start the on-demand downscaling",
)
run_chickadee.on_click(handle_run_chickadee)

run_finch = Button(
    description="Run Finch",
    button_style="info",
    disabled=False,
    tooltip="Click 'Run' to start the climate index calculations",
)
run_finch.on_click(handle_run_finch)

box_layout = Layout(
    display="flex", flex_flow="column", width="110%", align_items="center"
)
control_box = Box(
    children=[
        center_hover,
        center,
        clim_vars,
        dataset,
        technique,
        model,
        canesm5_run,
        scenario,
        period,
        run_chickadee,
        run_finch,
    ],
    layout=box_layout,
)

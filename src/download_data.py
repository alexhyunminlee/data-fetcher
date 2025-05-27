import os
import sys
import click
import zipfile
#AWS
import boto3
from botocore.config import Config
from botocore import UNSIGNED

# Baseline s3 download path
baseline_oedi_path = "nrel-pds-building-stock/end-use-load-profiles-for-us-building-stock"

@click.command()
@click.option('--output_path', required=True, type=click.Path(), help='Directory to download data into')
@click.option('--upgrade_id', required=True, type=click.Path(), help='Directory to download data into')
@click.option('--year', default="2024", show_default=True, help='Building data release year')
@click.option('--version', default="resstock_tmy3_release_2", show_default=True, help='Building data release version')
def download_data(output_path, upgrade_id, year, version):
    # Read stdin input. Assume it's a single building id
    building_id = int(sys.stdin.read().strip())
    upgrade_id = int(upgrade_id)
    download_name = f"bldg{building_id:07}-up{upgrade_id:02}"
    # Create directory for downloaded data
    os.makedirs(output_path, exist_ok=True)
    # Download data
    oedi_path = f"{baseline_oedi_path}/{year}/{version}/model_and_schedule_files/building_energy_models/"
    oedi_download_path = oedi_path + f"upgrade={upgrade_id}/{download_name}.zip"
    s3_client = boto3.client("s3", config=Config(signature_version=UNSIGNED))
    zip_filepath = f"{output_path}/bldg{building_id:07}-up{upgrade_id:02}.zip"
    s3_client.download_file("oedi-data-lake", oedi_download_path, zip_filepath)
    # Extract zip file
    with zipfile.ZipFile(zip_filepath, "r") as zip_ref:
        if year == "2024":
            zip_ref.extract("home.xml",output_path)
            zip_ref.extract("in.schedules.csv",output_path)            
        else:
            zip_ref.extract("in.xml",output_path)
            zip_ref.extract(".schedules.csv",output_path)
    os.remove(zip_filepath) # Remove zip file
    if year == "2024":
        os.rename(f"{output_path}/home.xml", f"{output_path}/bldg{building_id:07}-up{upgrade_id:02}.xml")
        os.rename(f"{output_path}/in.schedules.csv", f"{output_path}/bldg{building_id:07}-up{upgrade_id:02}_schedule.csv")
    else:
        os.rename(f"{output_path}/in.xml", f"{output_path}/bldg{building_id:07}-up{upgrade_id:02}.xml")
        os.rename(f"{output_path}/schedules.csv", f"{output_path}/bldg{building_id:07}-up{upgrade_id:02}_schedule.csv")

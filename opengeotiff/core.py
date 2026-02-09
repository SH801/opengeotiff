import os
import sys
import yaml
import requests
import rasterio
import geopandas as gpd
from rasterio.mask import mask as riomask
from rasterio.features import shapes
from shapely.geometry import shape

class OpenGeoTIFF:
    def __init__(self, config_path):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.source = self.config['source']
        self.cache_dir = self.config['cache_dir']
        self.clipping_path = self.config['clipping']
        self.output_name = self.config['output']
        self.val_min = self.config['mask']['min']
        self.val_max = self.config['mask']['max']
        
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)

    def run(self):
        # 1. Download
        filename = os.path.basename(self.source)
        local_tif = os.path.join(self.cache_dir, filename)
        
        if not os.path.exists(local_tif):
            print(f"[*] Downloading source: {self.source}")
            r = requests.get(self.source, stream=True)
            r.raise_for_status()
            with open(local_tif, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        else:
            print(f"[*] Using cached source: {local_tif}")

        # 2. Process Raster
        print(f"[*] Processing mask ({self.val_min} - {self.val_max})...")
        with rasterio.open(local_tif) as src:
            # Handle Clipping
            clip_gdf = gpd.read_file(self.clipping_path).to_crs(src.crs)
            geoms = clip_gdf.geometry.values
            
            out_image, out_transform = riomask(src, geoms, crop=True)
            data = out_image[0]

            # 3. Apply Mask Logic
            # Areas within range become 1, others are masked
            mask_condition = (data >= self.val_min) & (data <= self.val_max)
            binary_mask = mask_condition.astype('int16')

            # 4. Vectorize
            # We only want to create polygons for the '1' values (the insufficient areas)
            results = (
                {'properties': {'value': v}, 'geometry': s}
                for i, (s, v) in enumerate(shapes(binary_mask, mask=(binary_mask == 1), transform=out_transform))
            )

            # 5. Export
            print(f"[*] Vectorizing and saving to {self.output_name}...")
            gdf = gpd.GeoDataFrame.from_features(list(results), crs=src.crs)
            
            # Save to GPKG
            gdf.to_file(self.output_name, driver="GPKG")
            print("[+] Done.")

def main():
    # Check if a config file was provided
    if len(sys.argv) < 2:
        print("Usage: opengeotiff <config.yml>")
        sys.exit(1)

    config_path = sys.argv[1]
    
    # Check if the file actually exists
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        sys.exit(1)

    # Initialize and run
    app = OpenGeoTIFF(config_path)
    app.run()

if __name__ == "__main__":
    main()
import laspy
import lazrs
import rasterio
import numpy as np
import matplotlib.pyplot as plt
from rasterio.transform import from_origin

# Example usage from USGS LiDAR (https://apps.nationalmap.gov/lidar-explorer/#/)
with laspy.open('USGS_LPC_AK_GlacierBay_2019_B19_GB_00478.laz') as file:
    lidar_points = file.read()

# Extract x, y, and z coordinates
x_coords = lidar_points.x
y_coords = lidar_points.y
z_coords = lidar_points.z

# Define grid resolution
resolution = 1.0  # for example, 1 meter

# Calculate grid dimensions
xmin, ymin, xmax, ymax = [np.min(x_coords), np.min(y_coords), np.max(x_coords), np.max(y_coords)]
x_range = np.ceil((xmax - xmin) / resolution).astype(int)
y_range = np.ceil((ymax - ymin) / resolution).astype(int)

# Data type for the grid - float32 is usually a good choice
grid_dtype = np.float32

# Create the grid
grid = np.full((y_range, x_range), np.nan, dtype=grid_dtype)

# Print some statistics of z_coords for checking
print(f"Min elevation: {np.min(z_coords)}")
print(f"Max elevation: {np.max(z_coords)}")
print(f"Mean elevation: {np.mean(z_coords)}")

# Populate the grid with elevation values
for x, y, z in zip(x_coords, y_coords, z_coords):
    col = int((x - xmin) / resolution)
    row = int((y - ymin) / resolution)

    if 0 <= row < grid.shape[0] and 0 <= col < grid.shape[1]:
        grid[row, col] = z
# Export to TIFF
transform = from_origin(xmin, ymax, resolution, resolution)
with rasterio.open('lidar_dem.tif', 'w', driver='GTiff',
                   height=grid.shape[0], width=grid.shape[1],
                   count=1, dtype=str(grid.dtype), crs='+proj=latlong',
                   transform=transform) as dst:
    dst.write(grid, 1)

# Read DEM
with rasterio.open('lidar_dem.tif') as dem:
    elevation = dem.read(1)

# Plot DEM
plt.figure(figsize=(10, 10))
plt.imshow(grid, cmap='terrain')
plt.colorbar(label='Elevation')
plt.title('Digital Elevation Model')
plt.xlabel('X Coordinate')
plt.ylabel('Y Coordinate')
plt.show()


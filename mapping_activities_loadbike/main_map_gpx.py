from tqdm import tqdm
import os
import gpxpy
import folium
import gzip
from fit2gpx import Converter




def extract_gz_files(folder_path):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".gpx.gz") or file.endswith(".fit.gz"):
                file_path = os.path.join(root, file)
                output_path = os.path.splitext(file_path)[0]
                with gzip.open(file_path, 'rb') as f_in:
                    with open(output_path, 'wb') as f_out:
                        f_out.write(f_in.read())
                os.remove(file_path)
                print(f"Extracted {file_path} to {output_path}")



def main():
    # 地図を作成
    map_center = [35.681236, 139.767125]  # 東京駅の座標
    zoom_level = 10
    # 地形と道路の両方が見えるStamen Terrainタイルを使用
    m = folium.Map(location=map_center, zoom_start=zoom_level, tiles=None)
    folium.TileLayer(
        tiles="https://tiles.stadiamaps.com/tiles/stamen_terrain/{z}/{x}/{y}{r}.png",
        attr='&copy; <a href="https://www.stadiamaps.com/" target="_blank">Stadia Maps</a> '
             '&copy; <a href="https://www.stamen.com/" target="_blank">Stamen Design</a> '
             '&copy; <a href="https://openmaptiles.org/" target="_blank">OpenMapTiles</a> '
             '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        name='Stamen Terrain',
        max_zoom=20,
    ).add_to(m)
    folium.LayerControl().add_to(m)
    gpx_file_name_list = []

    # フォルダ内のGPXファイルとFITファイルのパスを取得
    #folder_path = r"C:\Users\phantasm\Downloads\gpx_test"
    folder_path = r"C:\Users\yosuk\Downloads\export_27348293(2)\activities"
    #folder_path = r"C:\Users\yosuk\Downloads\export_27348293(1)\activities"
    #folder_path = r"C:\Users\yosuk\Downloads\export_27348293\activities"
    #folder_path = r"E:\surface_download\export_27348293 (3)\activities"
    #folder_path = r"C:\Users\phantasm\Downloads\export_27348293 (3)\activities"
    #folder_path = r"C:\Users\phantasm\Downloads\export_27348293 (4)\activities"
    #folder_path = r"C:\Users\phantasm\Downloads\export_27348293 (4)\test"
    #folder_path = r"C:\Users\phantasm\Downloads\export_27348293 (2)\activities"
    #folder_path = r"C:\Users\phantasm\Downloads\export_27348293 (1)\activities"
    #folder_path = r"C:\Users\phantasm\Downloads\export_27348293 (1)\test"
    #folder_path = r"C:\Users\phantasm\Downloads\export_27348293 (1)\activities"
    extract_gz_files(folder_path)

    exclude_list = []
    exclude_list.append("1734329521.gpx") #入山峠
    exclude_list.append("3044268080.gpx") #榛名山

    fit_files = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith(".fit")]
    gpx_dir   = "all_gpx"
    conv = Converter()          # create standard converter object
    for fit_file in tqdm(fit_files):
        full_path_wo_ext, old_extension = os.path.splitext(fit_file)
        gpx_full_path = full_path_wo_ext + ".gpx"
        file_name_wo_ext = os.path.basename(full_path_wo_ext)
        out_gpx_full_path = gpx_dir + "/" + file_name_wo_ext + ".gpx"
        if(not (os.path.exists(gpx_full_path) or os.path.exists(out_gpx_full_path))):
            #print(f'Transforming {fit_file} --> {gpx_file}')
            conv.fit_to_gpx(f_in=fit_file, f_out=out_gpx_full_path)
    
    
    # GPXファイルごとに線を描画
    gpx_files = [os.path.join(gpx_dir, f) for f in os.listdir(gpx_dir) if f.endswith(".gpx")]
    for gpx_file in tqdm(gpx_files):
        gpx_file_basename = os.path.basename(gpx_file)
        if(gpx_file_basename in exclude_list):
            continue
        if(gpx_file_basename in gpx_file_name_list):
            continue
        else:
            gpx_file_name_list.append(os.path.basename(gpx_file))
            with open(gpx_file, "r", encoding="UTF-8") as f:
                gpx = gpxpy.parse(f)
                coords = []
                for track in gpx.tracks:
                    for segment in track.segments:
                        for point in segment.points:
                            coords.append([point.latitude, point.longitude])
                folium.PolyLine(
                    coords,
                    color='#e74c3c',
                    weight=4,
                    opacity=0.9,
                ).add_to(m)
    
    
    # 地図を保存
    m.save("map.html")


    
if __name__ == "__main__":
    main()
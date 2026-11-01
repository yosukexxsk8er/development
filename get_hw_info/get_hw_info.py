import platform
import subprocess

def get_cpu_model():
    system = platform.system()
    
    if system == "Windows":
        result = subprocess.run(['wmic', 'cpu', 'get', 'name'], stdout=subprocess.PIPE, text=True)
        lines = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        if len(lines) > 1:
            return lines[1]
    elif system == "Linux":
        result = subprocess.run(['lscpu'], stdout=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            if 'Model name:' in line:
                return line.split(':')[1].strip()
    else:
        return "Unsupported OS"

def get_motherboard_info():
    system = platform.system()
    info = {}
    
    if system == "Windows":
        result = subprocess.run(['wmic', 'baseboard', 'get', 'manufacturer,product'], stdout=subprocess.PIPE, text=True)
        lines = [line.strip() for line in result.stdout.split('\n') if line.strip()]
        if len(lines) > 1:
            manufacturer, product = lines[1].rsplit(' ', 1)
            info['Manufacturer'] = manufacturer.strip()
            info['Product Name'] = product.strip()
    elif system == "Linux":
        result = subprocess.run(['sudo', 'dmidecode', '-t', 'baseboard'], stdout=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            if line.strip().startswith('Manufacturer:'):
                info['Manufacturer'] = line.split(':')[1].strip()
            elif line.strip().startswith('Product Name:'):
                info['Product Name'] = line.split(':')[1].strip()
            elif line.strip().startswith('Version:'):
                info['Version'] = line.split(':')[1].strip()
    else:
        info['Error'] = "Unsupported OS"
    
    return info

cpu_model = get_cpu_model()
motherboard_info = get_motherboard_info()

print(f"CPU Model: {cpu_model}")
print(f"Motherboard Manufacturer: {motherboard_info.get('Manufacturer')}")
print(f"Motherboard Product Name: {motherboard_info.get('Product Name')}")
print(f"Motherboard Version: {motherboard_info.get('Version')}")

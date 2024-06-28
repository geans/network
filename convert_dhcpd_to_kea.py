import json


def parse_dhcpd_conf(file_path):
    networks = []
    current_network = {}
    current_subnet = {}
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith('shared-network'):
                if current_network:
                    networks.append(current_network)
                current_network = {
                    "name": line.split()[1].strip('{}'),
                    "subnet4": []
                }
            elif line.startswith('subnet'):
                if current_subnet:
                    current_network["subnet4"].append(current_subnet)
                parts = line.split()
                mask = sum([bin(int(i)).count('1') for i in parts[3].split('.')])
                current_subnet = {
                    "subnet": f"{parts[1]}/{mask}",
                    "pools": [],
                    "option-data": []
                }
            elif line.startswith('range'):
                parts = line.split()
                current_subnet["pools"].append({"pool": f"{parts[1]} - {parts[2].replace(';', '')}"})
            elif line.startswith('option'):
                parts = line.split()
                data = [i.replace('"', '').replace(';', '') for i in parts[2:]]
                option = {
                    "name": parts[1],
                    "data": ' '.join(data)
                }
                current_subnet["option-data"].append(option)
            elif line.startswith('}'):
                if current_subnet:
                    current_network["subnet4"].append(current_subnet)
                    current_subnet = {}
        if current_network:
            networks.append(current_network)
    
    return networks


def generate_kea_config(networks):
    kea_config = {
        "Dhcp4": {
            "shared-networks": networks,
            # [en] Add other KEA settings here if necessary
            # [pt-br] Adicione outras configurações do KEA aqui, se necessário
        }
    }
    return kea_config


def main():
    input_file = 'shared-network.only.conf'
    output_file = 'kea-dhcp4.json'
    
    networks = parse_dhcpd_conf(input_file)
    kea_config = generate_kea_config(networks)
    
    with open(output_file, 'w') as file:
        json.dump(kea_config, file, indent=2)


if __name__ == "__main__":
    main()

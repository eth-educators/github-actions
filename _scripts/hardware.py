import utilities
import requests
import json


script_id = "hardware"



def get_hardware_data():
  if utilities.use_test_data:
    response = {'status': 200, 'attempts': 1, 'data': [{"name":"Modem / Router","index":1,"products":[{"id":None,"name":"Your existing modem/router","price":0}],"usage":"required","min_specs":None,"guide":None},{"name":"Computer","index":2,"products":[{"id":"B09KNK27M2","name":"Intel NUC 11 NUC11PAHi7 Barebone Mini-PC","details":"Core i7-1165G7","link":"https://www.amazon.com/dp/B09KNK27M2/","price":395},{"id":"N82E16856110250","name":"ASUS ExpertCenter PN64 Barebone Mini-PC","details":"Intel Core i3-1220P","link":"https://www.newegg.com/p/N82E16856110250","price":358}],"usage":"required","min_specs":None,"guide":None},{"name":"SSD","index":3,"products":[{"id":"B08RK2SR23","name":"Samsung 980 PRO","details":"2TB, PCIe 4.0, M2","link":"https://www.amazon.com/dp/B08RK2SR23/","price":167},{"id":"N82E16820147796","name":"Samsung 980 PRO","details":"2TB, PCIe 4.0, M2","link":"https://www.newegg.com/p/N82E16820147796","price":167}],"usage":"required","min_specs":">=2TB","guide":"https://www.youtube.com/watch?v=04K8OUOMHGM"},{"name":"RAM","index":4,"products":[{"id":"B07ZLC7VNH","name":"Crucial RAM CT32G4SFD832A","details":"32GB DDR4 3200MHz CL22","link":"https://www.amazon.com/dp/B07ZLC7VNH","price":68}],"usage":"required","min_specs":">=32GB","guide":"https://www.youtube.com/watch?v=04K8OUOMHGM"},{"name":"UPS","index":5,"products":[{"id":"B0030SL08A","name":"CyberPower CP425SLG Standby UPS System","details":None,"link":"https://www.amazon.com/dp/B0030SL08A/","price":60},{"id":"N82E16842102117","name":"CyberPower CP425SLG Standby UPS System","details":None,"link":"https://www.newegg.com/p/N82E16842102117","price":74},{"id":"cp550slg","name":"CyberPower CP425SLG Standby UPS System","details":None,"link":"https://www.cyberpowersystems.com/product/ups/standby/cp550slg/","price":74}],"usage":"recommended","min_specs":None,"guide":"https://github.com/trevhub/guides/blob/main/CheapUPS.md"},{"name":"Smart Plug","index":6,"products":[{"id":"B091699Z3W","name":"Kasa Smart Plug Ultra Mini","details":None,"link":"https://www.amazon.com/dp/B091699Z3W","price":10}],"usage":"optional","min_specs":None,"guide":"https://www.wintips.org/setup-computer-to-auto-power-on-after-power-outage/"}]}
    utilities.log(response, context=f"{script_id}__get_hardware_data")
    return response
  else:
    url = "https://raw.githubusercontent.com/eth-educators/website/main/_data/hardware.yml"
    response = utilities.fetch(url, "GET", data_type="yaml", context=f"{script_id}__get_hardware_data")
    return response

def get_unavailable_products():
  if utilities.use_test_data:
    return "1VK-001S-02DH9, "
  else:
    unavailable_products = utilities.read_file("_data/hardware-unavailable.txt", file_type="text", context=f"{script_id}__get_unavailable_data")
    return unavailable_products

def process_hardware_data(hardware_data, unavailable_products):
  updated_unavailable_products = ""
  components_unavailable = []
  for component in hardware_data:
    component_products_unavailable = 0
    for product in component["products"]:
      if "link" in product:
        response = requests.get(product["link"])
        if (response.status_code == 200):
          if "amazon.com" in product["link"]:
            if "We don't know when or if this item will be back in stock.".encode() in response.content:
              updated_unavailable_products += f'{product["id"]}, '
              component_products_unavailable += 1
          elif "newegg.com" in product["link"]:
            if "out of stock".encode() in response.content:
              updated_unavailable_products += f'{product["id"]}, '
              component_products_unavailable += 1
        elif (product["id"] in unavailable_products):
          updated_unavailable_products += f'{product["id"]}, '
          component_products_unavailable += 1
    if component_products_unavailable == len(component["products"]):
      components_unavailable.append(component["name"])
  utilities.log(updated_unavailable_products, context=f"{script_id}__updated_unavailable_products")
  # if len(updated_unavailable_products) > 0:
  #   msg = f"Hardware unavailable: {updated_unavailable_products}"
  #   utilities.sendDiscordMsg(utilities.DISCORD_WEBSITE_WEBHOOK, msg)
  if len(components_unavailable) > 0:
    msg = f"Hardware unavailable: {', '.join(components_unavailable)}"
    utilities.sendDiscordMsg(utilities.DISCORD_WEBSITE_WEBHOOK, msg)
  else:
    print("no hardware unavailable")
  return updated_unavailable_products

def save_unavailable_products_data(updated_unavailable_products):
  utilities.save_to_file(f"_data/hardware-unavailable.txt", updated_unavailable_products, context=f"{script_id}__save_unavailable_products_data")



def check_hardware_availability():
  hardware_data = get_hardware_data()
  if (hardware_data["status"] == 200):
    unavailable_products = get_unavailable_products()
    updated_unavailable_products = process_hardware_data(hardware_data["data"], unavailable_products)
    save_unavailable_products_data(updated_unavailable_products)
  else: 
    error = f"Bad response"
    utilities.log(f"{error}: {script_id}")
    utilities.report_error(error, context=f"{script_id}__check_hardware_availability")
    return





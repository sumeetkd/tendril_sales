import json


class salemodules:
    """
    UI facing modules meant collect the details of standard modules from a json
    and feed it to the user interface.
    """

    def __init__(self):
        """
        Initialized using the location of standard modules
        """
        file = open("modules.json","r")
        self.std_modules = json.load(file)

    def module_list(self):
        """
        :param self: self.std_modules provides the list of modules accessible
        :return: list of items for which quotations can be issued using this module
        """
        itemlist= []
        for items in self.std_modules:
            itemlist.append(items['modulename'])
        return itemlist

class module:

    def __init__(self,name,pincode):
        file = open("modules.json", "r")
        self.file = json.load(file)
        self.module = (item for item in self.file if item["modulename"] == name)
        self.pincode = pincode

    def __location__(self):
        """
        Location function. Uses the pincode of the delivery location to determine the value of
        Freight, Installation, Commissioning and Training
        OR
        Installation, Commissioning and Training
        :return:
        """
        state = self.pincode/10000
        if state is 11:
            cost = 'INR 10000'
        elif state in (range(35,40,1) + range(40,87,1)):
            cost = 'INR 35000'
        else:
            cost = 'INR 25000'
        return cost


    def constituentitems(self):
        """
        Generates the line items that will be used to build the quote.
        - Creates list of products that form part of the quotation and the optionals
        - Addons computed using the __location__() module
        - Discounts added as per the json definition
        - Persona added as per product
        :return:
        """
        productlist = []
        addonlist = []
        discountlist = []
        optional_table = False
        for item in self.module:
            for product in item["items"]:
                optional_status = (False if product["optional"] == 'False' else True)
                optional_table = optional_table or optional_status
                productlist.append((str(product["name"]), int(product["quantity"]), optional_status))
            for addon in item["addons"]:
                print(addon["name"])
                if (str(addon["name"]) == "Freight, Installation, Training and Commissioning") | (str(addon["name"]) == "Installation, Training and Commissioning"):
                    addonlist.append((str(addon["name"]), self.__location__(), False if addon["optional"] == 'False' else True))
                else:
                    addonlist.append((str(addon["name"]), str(addon["cost"]),False if addon["optional"] == 'False' else True))
            for discount in item["discounts"]:
                discountlist.append(
                    (str(discount["name"]), str(discount["value"]), lambda x: not x.info.is_consumable and not x.info.is_third_party))
            print(discountlist)
            persona = [item["persona"]["company"],item["persona"]["signatory"]]
            print(persona)
        return productlist, addonlist, discountlist, persona, optional_table

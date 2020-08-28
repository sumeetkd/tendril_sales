from __future__ import print_function
from warnings import warn
from tendril.dox import render
from tendril.libraries import products
from tendril.pricing.collector import PriceCollector
from tendril.pricing.tax import TaxDefinitionList
from tendril.utils.types.time import DateSpan
from tendril.identity import persona as identity
from salemodules import module
import os

class quote:

    def __init__(self, result):
        """

        :param result:
        """
        self.target_warranty_yrs= DateSpan(result['warranty']+'yr')
        self.warranty_option = False if result['warranty_optional'] == 'False' else True
        self.amc_option = False if result['amc_optional'] == 'False' else True
        self.client = str(result['client_name'])
        self.client_address = [str(result['client_address_1']),str(result['client_address_2'])]
        self.pincode = int(result['pincode'])
        self.quote_validity = str(result['quote_validity'])
        self.docid = str(result['doc_id'])
        self.modulename = str(result['module'])
        self.tax_exemption = False if result['dsir'] == 'False' else True
        system = module(self.modulename, self.pincode)
        self.products, self.addons, self.discounts, self.persona = system.constituentitems()

    def __taxes__(self):
        if (self.pincode/10000 == 11):
            if self.tax_exemption == True:
                return TaxDefinitionList([
                                {'tax': 'CGST', 'rate': '2.5%'},
                                {'tax': 'SGST', 'rate': '2.5%'}])
            else:
                return TaxDefinitionList([
                                {'tax': 'CGST', 'rate': '9%'},
                                {'tax': 'SGST', 'rate': '9%'}])
        else:
            if self.tax_exemption == True:
                return TaxDefinitionList([{'tax': 'IGST', 'rate': '5%'}])
            else:
                return TaxDefinitionList([{'tax': 'IGST', 'rate': '18%'}])

    def pricing_calculation(self):
        items = self.products
        addons = self.addons
        override_taxes = self.__taxes__()
        print(override_taxes)
        #override_taxes = TaxDefinitionList([{'tax': 'IGST', 'rate': '5%'}])
        discounts = self.discounts
        warranty_discount = ('0%', 'Warranty Discount')


        c = PriceCollector()
        for product, qty, optional in items:
            p = products.get_product_by_ident(product)
            p.pricing.qty = qty

            for name, rate, criteria in discounts:
                if (criteria(p) & ~optional):
                    p.apply_discount(rate, name)

            if override_taxes:
                p.pricing.override_taxes(override_taxes)

            w_yrs = self.target_warranty_yrs
            w_yrs -= p.info.warranty.std

            if ((w_yrs > DateSpan('0yr')) and (p.info.warranty.ext_max > 0)):
                if p.info.warranty.ext_max < w_yrs:
                    p.add_extended_warranty(p.info.warranty.ext_max,
                                            discount=warranty_discount, optional=self.warranty_option)
                    w_yrs -= p.info.warranty.ext_max
                    if p.info.warranty.amc_max < w_yrs:
                        p.add_amc(p.info.warranty.amc_max, optional=self.amc_option)
                        w_yrs -= p.info.warranty.amc_max
                    else:
                        p.add_amc(w_yrs, optional=self.amc_option)
                        w_yrs = 0
                else:
                    p.add_extended_warranty(w_yrs,
                                            discount=warranty_discount, optional=self.warranty_option)
                    w_yrs = 0
                if w_yrs:
                    warn('Warranty on {0} is less than the required by {1}'.format(product, w_yrs))

            c.add_item(p, optional=optional)

        for addon, price, optional in addons:
            c.include_addon(addon, price=price, optional=optional)

        return c


    def print_quote(self,pricing_collection):
        workspace = os.getcwd()
        client = {'name': self.client,
                  'add' : self.client_address}
        identity_name = self.persona[0]
        signatory_id = self.persona[1]
        persona = getattr(identity, identity_name)
        persona.signatory = signatory_id
        offered_solution = self.modulename
        stage = {
                    'docid': self.docid,
                    'quote': pricing_collection,
                    'quote_validity': self.quote_validity,
                    'client': client,
                    'persona': persona,
                    'product': offered_solution,
                }
        targets = ['sales/quotation.tex']
        for target in targets:
            outfpath = os.path.join(workspace, os.path.splitext(os.path.split(target)[1])[0] + '.pdf')
            render.render_pdf(stage, target, outfpath, remove_sources=False)

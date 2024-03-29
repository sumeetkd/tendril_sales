from flask import Flask, render_template, request, send_from_directory
import quotation
from quotation import quote
from salemodules import salemodules
from datetime import datetime
modules = salemodules()
app = Flask(__name__)
app.config["latex"] = "/home/sumeetkd/codes/Quazar/UI"


@app.route('/quotation_form')
def quotation_form():
    """
    Simple form that collects the parameters for issuing a Quote.
    The variables are defined in the quote_form.html.
    Variable name is defines using name=XYZ
    List of standard modules are extracted from module_list()
    :return:
    """
    itemlist = modules.module_list()
    return render_template('quote_form.html', itemlist = itemlist)

@app.route('/quote_confirmation',methods = ['POST', 'GET'])
def issue_quote():
    """
    On submission of the form on /quotation_form, the variables are submitted to create an instance of quotation.quote.
    Some of the above variables need to be processed to generate pricing using the pricing_calculation().
    Which can then be passed on to the print_quote() function which provides the pdf
    :return: Displays the variables in an html page
    """
    if request.method == 'POST':
       result = request.form.to_dict()
       print(result)
       reload(quotation)
       quote_details = quote(result)
       pricing = quote_details.pricing_calculation()
       quote_details.print_quote(pricing)
       return render_template("confirmation.html",result = result)

@app.route("/download_quote")
def get_file():
    """
    Download the quotation
    :return:
    """
    now = datetime.now()
    file = now.strftime("%Y%m%d%H%M%S") + '.pdf'
    print(file)
    try:
        return send_from_directory(app.config["latex"], filename='quotation.pdf', as_attachment=True, attachment_filename=file, cache_timeout=0)
    except FileNotFoundError:
        abort(404)

if __name__ == '__main__':
    app.run(debug=False, host= '0.0.0.0', port=5124)
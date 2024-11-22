from flask import Flask
from app.routes import bp as routes_bp
from app.utils.file_utils import download_file


url = "https://rejestry.ezdrowie.gov.pl/api/rpl/medicinal-products/public-pl-report/get-csv"
file_path = "./downloaded_files/meds_list.csv"

app = Flask(__name__)
app.register_blueprint(routes_bp)


download_file(url, file_path)

if __name__ == "__main__":
    app.run()

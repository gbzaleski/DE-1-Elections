YEARS = [2019, 2023]

LINKS_BY_YEAR = {
    2019: [
        "https://wybory.gov.pl/sejmsenat2019/data/csv/okregi_sejm_csv.zip",
        "http://wybory.gov.pl/sejmsenat2019/data/csv/wyniki_gl_na_listy_po_okregach_sejm_csv.zip"],
    2023: [
        "http://wybory.gov.pl/sejmsenat2023/data/csv/okregi_sejm_csv.zip",
        "http://wybory.gov.pl/sejmsenat2023/data/csv/wyniki_gl_na_listy_po_okregach_sejm_csv.zip"
    ]
}

FILENAMES_BY_YEAR = {
    2019: {
        "results": "wyniki_gl_na_listy_po_okregach_sejm.csv",
        "districts": "okregi_sejm.csv"
    },
    2023: {
        "results": "wyniki_gl_na_listy_po_okregach_sejm_utf8.csv",
        "districts": "okregi_sejm_utf8.csv"
    }
}

MINIO_DEFAULT_SERVER_URL = "localhost:9000"
MINIO_DEFAULT_USER = "admin"
MINIO_DEFAULT_PASSWORD = "adminadmin"

CONSTITUENCIES = 41
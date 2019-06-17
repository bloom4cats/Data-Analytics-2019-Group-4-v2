import linecache
import random
import io
import pandas as pd
import numpy as np


def get_line_count(input_file):
    """Count number of lines in a file"""
    count = 0
    with open(input_file) as infile:
        for line in infile:
            count += 1
    return count


def sample_file(input_file, output_file, fraction=0.1):
    """Exctract a subset of lines from a file"""
    total_line_count = get_line_count(input_file)
    sample_line_count = int(fraction * total_line_count)  # fraction of total
    random.seed(
        12345
    )  # set an arbitrary number to force same sample of rows each time
    sample_line_numbers = random.sample(
        range(1, total_line_count), sample_line_count
    )  # sample of line numbers
    sample_line_numbers.sort()
    sample_line_numbers.insert(0, 0)
    with open(output_file, "w") as outfile:
        for line_number in sample_line_numbers:
            line = linecache.getline(input_file, line_number + 1)
            outfile.write(line)
    return


def clean_franklin(in_file):
    subset_file = pd.read_csv(in_file)
    sel_columns = [
        "ParcelNumber",
        "APPRLND",
        "APPRBLD",
        "LandUse",
        "Cauv",
        "SCHOOL",
        "HOMESTD",
        "TRANDT",
        "NAME1",
        "NAME2",
        "NBRHD",
        "PCLASS",
        "PRICE",
        "ACREA",
        "ROOMS",
        "BATHS",
        "ANN_TAX",
        "DESCR1",
        "TAXDESI",
        "AREA2",
        "DWELTYP",
        "COND",
        "Grade",
        "USPS_CITY",
        "HBATHS",
        "BEDRMS",
        "AIRCOND",
        "FIREPLC",
        "YEARBLT",
        "WALL",
    ]
    df = subset_file[sel_columns].copy()
    df = df[df.PCLASS == "R"]
    df.drop(["PCLASS"], axis=1, inplace=True)
    df["APPRBLD"] = df.APPRBLD.astype(int)
    df = df[df.APPRBLD > 0]
    df["APPRLND"] = df.APPRLND.astype(int)
    df = df[df.APPRLND > 0]
    df["Bathrooms"] = df.BATHS.fillna(0) + 0.5 * df.HBATHS.fillna(0)
    df.drop(["BATHS", "HBATHS"], axis=1, inplace=True)
    df.FIREPLC.fillna(value=0, inplace=True)
    df["Fireplaces"] = df.FIREPLC.astype(bool)
    return df


def clean_licking(in_file):
    old_value = "430 Resturant; cafteria and/or bar"
    new_value = "430 Resturant, cafeteria and/or bar"
    with open(in_file) as infile:
        content = infile.read()
    content = content.replace(old_value, new_value)
    df = pd.read_csv(io.StringIO(content), delimiter=";", engine="python")
    # replace all the leading 'fld' portion of every column header to simplify outputs
    df.columns = df.columns.str.replace("fld", "")
    sel_styles = [
        "Single Family",
        "MFD Home",
        "Tri-Level",
        "Duplex",
        "Bi-Level",
        "Multi-Level",
        "Condominum",
        "Mobile Home",
        "Triplex",
        "4-Level",
    ]
    sel_columns = [
        "ParcelNo",
        "Owner",
        "Grade",
        "Condition",
        "MarketLand",
        "LUC",
        "SchoolDistrict",
        "TaxDistrict",
        "Neighborhood",
        "Subtotal",
        "CAUVTotal",
        "LegalDesc",
        "PropertyType",
        "Exterior",
        "MarketImprov",
        "SalesDate1",
        "SalesPrice1",
        "AcreageTotal",
        "FinishedLivingArea",
        "Rooms",
        "Bedrooms",
        "FullBaths",
        "HalfBaths",
        "OtherBaths",
        "Heating",
        "Cooling",
        "FireplaceOpenings",
        "YearBuilt",
        "MailingAddress5",
    ]
    df = df[df.Style.isin(sel_styles)].copy()
    df = df[sel_columns]
    df["Bathrooms"] = (
        df.FullBaths.fillna(0)
        + 0.5 * df.HalfBaths.fillna(0)
        + 0.25 * df.OtherBaths.fillna(0)
    )
    df.drop(["FullBaths", "HalfBaths", "OtherBaths"], axis=1, inplace=True)
    df.Heating = df.Heating != "No Heat"
    df.Cooling = df.Cooling == "Central"
    df.FireplaceOpenings.fillna(0, inplace=True)
    df["Fireplaces"] = df.FireplaceOpenings.astype(bool)
    df.rename(
        {
            "ParcelNo": "ParcelNumber",
            "Owner": "OwnerName",
            "MarketLand": "AppraisedTaxableLand",
            "MarketImprov": "AppraisedTaxableBuilding",
            "Subtotal": "AnnualTaxes",
            "Neighborhood": "NeighborhoodCode",
            "CAUVTotal": "CAUV",
            "LegalDesc": "LegalDescription",
            "PropertyType": "DwellingType",
            "Exterior": "WallType",
            "SalesDate1": "TransferDate",
            "SalesPrice1": "SalePrice",
            "AcreageTotal": "Acreage",
            "FinishedLivingArea": "Area",
            "Heating": "Heat",
            "Cooling": "AirConditioning",
            "MailingAddress5": "USPSCity",
            "LUC": "LandUse",
        },
        axis=1,
        inplace=True,
    )
    df["County"] = "Licking"
    return df


def clean_fairfield(in_file):
    df = geopandas.read_file(in_file)
    sel_columns = [
        "PARID",
        "ACRES",
        "APRLAND",
        "APRBLDG",
        "SFLA",
        "RMBED",
        "FIXBATH",
        "FIXHALF",
        "LEGAL1",
        "OWN1",
        "OWN2",
        "WBFP_O",
        "GRDFACT",
        "LUC",
        "MCITYNAME",
        "YRBLT",
        "RMTOT",
        "HEAT",
        "PRICE",
        "EXTWALL",
        "TRANSDT",
    ]
    df = df[df.CLASS == "R"][sel_columns].copy()
    df["Bathrooms"] = df.FIXBATH + 0.5 * df.FIXHALF
    df.drop(["FIXBATH", "FIXHALF"], axis=1, inplace=True)
    df = df[df.HEAT.notna()]
    df = df[df.HEAT != ""]
    df["AirConditioning"] = df.HEAT == "3"
    df.HEAT = df.HEAT != "1"
    df.rename(
        {
            "PARID": "ParcelNumber",
            "ACRES": "Acreage",
            "APRLAND": "AppraisedTaxableLand",
            "APRBLDG": "AppraisedTaxableBuilding",
            "SFLA": "Area",
            "RMBED": "Bedrooms",
            "LEGAL1": "LegalDescription",
            "OWN1": "OwnerName",
            "WBFP_O": "FireplaceOpenings",
            "GRDFACT": "Grade",
            "LUC": "LandUse",
            "MCITYNAME": "USPSCity",
            "YRBLT": "YearBuilt",
            "RMTOT": "Rooms",
            "HEAT": "Heat",
            "PRICE": "SalePrice",
            "EXTWALL": "WallType",
            "TRANSDT": "TransferDate",
        },
        axis=1,
        inplace=True,
    )
    t2 = len(df)
    s2 = int(0.1 * t2)  # fraction of total
    rows = random.sample(range(df.index[0], t2), s2)
    df = df.iloc[rows]

    import numpy as np

    df["AnnualTaxes"] = np.nan
    df["CAUV"] = np.nan
    df["Condition"] = np.nan
    df["County"] = "Fairfield"
    df["DwellingType"] = np.nan
    df["FireplacesFlag"] = df.FireplaceOpenings > 0
    df["NeighborhoodCode"] = np.nan
    df.drop(["OWN2"], axis=1, inplace=True)
    df["SchoolDistrict"] = np.nan
    df["TaxDesignation"] = np.nan

    return df


def mod_date(df, x):
    df.loc[:, "month"] = pd.to_datetime(df["month"], format="%Y-%m-%d", errors="coerce")
    # df[x] = pd.to_datetime(df[x], format='%Y-%m-%d', errors='coerce')
    return df

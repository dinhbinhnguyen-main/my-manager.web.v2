import os
from enum import Enum

# --- SYSTEM SETTINGS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "repositories", "database", "real_estate.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
DEFAULT_LOGO = "/static/uploads/default_logo.png"


# --- REAL ESTATE CONSTANTS ---
class Product__Status(str, Enum):
    SELLING = "selling"
    SOLD = "sold"
    HIDDEN = "hidden"
    INACTIVE = "inactive"
    AVAILABLE_DATE = "available_date"


class RealEstateProduct__TransactionType(str, Enum):
    SALE = "sale"
    RENT = "rent"
    TRANSFER = "transfer"


class RealEstateProduct__Province(str, Enum):
    LAM_DONG = "lam_dong"


class RealEstateProduct__District(str, Enum):
    DA_LAT = "da_lat"


class RealEstateProduct__Ward(str, Enum):
    PHUONG_1 = "phuong_1_xuan_huong"
    PHUONG_2 = "phuong_2_xuan_huong"
    PHUONG_3 = "phuong_3_xuan_huong"
    PHUONG_4 = "phuong_4_xuan_huong"
    PHUONG_5 = "phuong_5_cam_ly"
    PHUONG_6 = "phuong_6_cam_ly"
    PHUONG_7 = "phuong_7_lang_biang"
    PHUONG_8 = "phuong_8_lam_vien"
    PHUONG_9 = "phuong_9_lam_vien"
    PHUONG_10 = "phuong_10_xuan_huong"
    PHUONG_11 = "phuong_11_xuan_truong"
    PHUONG_12 = "phuong_12_lam_vien"
    XUAN_TRUONG = "xa_xuan_truong"
    XUAN_THO = "xa_xuan_tho"
    TA_NUNG = "xa_ta_nung"
    TRAM_HANH = "xa_tram_hanh"
    LAC_DUONG = "thi_tran_lac_duong"


class RealEstateProduct__Category(str, Enum):
    TOWNHOUSE = "townhouse"
    STREET_FRONT_HOUSE = "street_front_house"
    APARTMENT_CONDO = "apartment_condo"
    VILLA = "villa"
    LAND_PLOT = "land_plot"
    WAREHOUSE_YARD = "warehouse_yard"
    BUSINESS_PREMISES = "business_premises"
    HOTEL = "hotel"
    HOMESTAY = "homestay"


class RealEstateProduct__Unit(str, Enum):
    BILLION = "billion"
    MILLION = "million"
    MILLION_PER_MONTH = "million_per_month"


class RealEstateProduct__Legal(str, Enum):
    VI_BANG_PURCHASE = "vi_bang_purchase"
    SHARED_AGRICULTURAL_DEED = "shared_agriculture_deed"
    DECENTRALIZED_AGRICULTURAL_DEED = "decentralized_agriculture_deed"
    PRIVATE_AGRICULTURAL_DEED = "private_agriculture_deed"
    SHARED_CONSTRUCTION_DEED = "shared_construction_deed"
    DECENTRALIZED_CONSTRUCTION_DEED = "decentralized_construction_deed"
    PRIVATE_CONSTRUCTION_DEED = "private_construction_deed"


class RealEstateProduct__BuildingLine(str, Enum):
    CAR_ACCESS_ROAD = "car_access_road"
    MOTORBIKE_ACCESS_ROAD = "motorbike_access_road"


class RealEstateProduct__Furniture(str, Enum):
    NO_FURNITURE = "no_furniture"
    BASIC_FURNITURE = "basic_furniture"
    FULL_FURNITURE = "full_furniture"

"""
utils/i18n.py
Central Internationalization & Enum Dictionary Engine.
Cung cấp từ điển chuẩn hóa và đa ngôn ngữ (Tiếng Việt 🇻🇳 và Tiếng Anh 🇬🇧)
cho tất cả các trường hiển thị, giá trị Enum và nhãn giao diện của hệ thống.
"""

from typing import Any, Optional, Dict, List, Tuple, Type
from enum import Enum


class I18nManager:
    """
    Quản lý tập trung ngôn ngữ và từ điển dịch thuật cho các Enum và nhãn hệ thống.
    """

    _instance: Optional["I18nManager"] = None

    DEFAULT_LANGUAGE = "vi"
    SUPPORTED_LANGUAGES = {
        "vi": "Tiếng Việt 🇻🇳",
        "en": "English 🇬🇧",
    }

    def __init__(self) -> None:
        self._current_lang = self.DEFAULT_LANGUAGE
        self._init_catalogs()

    @classmethod
    def get_instance(cls) -> "I18nManager":
        if cls._instance is None:
            cls._instance = I18nManager()
        return cls._instance

    @property
    def current_language(self) -> str:
        return self._current_lang

    def set_language(self, lang: str) -> None:
        """
        Thay đổi ngôn ngữ hiển thị mặc định của hệ thống.
        """
        if lang in self.SUPPORTED_LANGUAGES:
            self._current_lang = lang

    def t(self, key: str, default: Optional[str] = None, lang: Optional[str] = None) -> str:
        """
        Tra cứu nhãn giao diện theo mã khóa (UI label key).
        """
        target_lang = lang or self._current_lang
        catalog = self._ui_translations.get(target_lang, {})
        if key in catalog:
            return catalog[key]
        fallback = self._ui_translations.get("en", {}).get(key)
        return fallback if fallback is not None else (default if default is not None else key)

    def tr_enum(
        self,
        value: Any,
        lang: Optional[str] = None,
        enum_cls: Optional[Type[Enum]] = None,
    ) -> str:
        """
        Dịch giá trị Enum (hoặc chuỗi mã Enum) sang nhãn hiển thị người dùng.
        Hỗ trợ:
        - Enum instance (ví dụ: PropertyType.TOWNHOUSE)
        - Giá trị chuỗi (ví dụ: 'townhouse', 'north', 'sale')
        - Qualified key (ví dụ: 'PropertyType.townhouse')
        """
        if value is None:
            return ""

        target_lang = lang or self._current_lang

        # Lấy giá trị chuỗi
        raw_val = value.value if isinstance(value, Enum) else str(value).strip()
        if not raw_val:
            return ""

        # Xác định tên class Enum nếu có
        cls_name = None
        if isinstance(value, Enum):
            cls_name = value.__class__.__name__
        elif enum_cls is not None:
            cls_name = enum_cls.__name__

        # 1. Tra cứu theo Qualified key: "ClassName.value"
        if cls_name:
            qualified_key = f"{cls_name}.{raw_val}"
            if qualified_key in self._enum_translations:
                trans = self._enum_translations[qualified_key]
                return trans.get(target_lang) or trans.get("vi") or trans.get("en") or raw_val

        # 2. Tra cứu theo raw value
        if raw_val in self._enum_translations:
            trans = self._enum_translations[raw_val]
            return trans.get(target_lang) or trans.get("vi") or trans.get("en") or raw_val

        # 3. Tra cứu theo dạng chữ thường
        lower_val = raw_val.lower()
        if lower_val in self._enum_translations:
            trans = self._enum_translations[lower_val]
            return trans.get(target_lang) or trans.get("vi") or trans.get("en") or raw_val

        # 4. Fallback: Làm đẹp chuỗi gốc (snake_case -> Title Case)
        return raw_val.replace("_", " ").title()

    def get_enum_dict(
        self,
        enum_cls: Type[Enum],
        lang: Optional[str] = None,
    ) -> Dict[str, str]:
        """
        Trả về từ điển {giá_trị_enum: nhãn_hiển_thị} cho toàn bộ các mục trong một Enum class.
        """
        target_lang = lang or self._current_lang
        result: Dict[str, str] = {}
        for member in enum_cls:
            result[member.value] = self.tr_enum(member, lang=target_lang, enum_cls=enum_cls)
        return result

    def get_enum_choices(
        self,
        enum_cls: Type[Enum],
        lang: Optional[str] = None,
    ) -> List[Tuple[str, str]]:
        """
        Trả về danh sách tuple (giá_trị, nhãn_hiển_thị) dùng cho thẻ select hoặc form option.
        """
        target_lang = lang or self._current_lang
        return [
            (member.value, self.tr_enum(member, lang=target_lang, enum_cls=enum_cls))
            for member in enum_cls
        ]

    def _init_catalogs(self) -> None:
        """
        Khởi tạo từ điển dịch thuật cho các Enum và nhãn hệ thống.
        """
        self._enum_translations: Dict[str, Dict[str, str]] = {
            # ---------------------------------------------------------------
            # 1. UserRole - Phân quyền người dùng
            # ---------------------------------------------------------------
            "admin": {"vi": "Quản trị viên", "en": "Administrator"},
            "manager": {"vi": "Trưởng nhóm", "en": "Manager"},
            "member": {"vi": "Nhân viên chính thức", "en": "Official Member"},
            "probation": {"vi": "Nhân viên thử việc", "en": "Probationary Staff"},
            "unknown": {"vi": "Chưa xác định", "en": "Unknown"},

            # ---------------------------------------------------------------
            # 2. ApprovalStatus - Trạng thái phê duyệt kiểm soát chất lượng
            # ---------------------------------------------------------------
            "draft": {"vi": "Bản nháp", "en": "Draft"},
            "pending": {"vi": "Chờ duyệt", "en": "Pending Approval"},
            "approved": {"vi": "Đã duyệt", "en": "Approved"},
            "rejected": {"vi": "Bị từ chối", "en": "Rejected"},

            # ---------------------------------------------------------------
            # 3. PendingAction - Hành động đề xuất chờ duyệt
            # ---------------------------------------------------------------
            "none": {"vi": "Không có", "en": "None"},
            "create": {"vi": "Đề xuất tạo mới", "en": "Create Request"},
            "update": {"vi": "Đề xuất cập nhật", "en": "Update Request"},
            "delete": {"vi": "Đề xuất xóa", "en": "Delete Request"},

            # ---------------------------------------------------------------
            # 4. ProductStatus - Trạng thái kinh doanh sản phẩm
            # ---------------------------------------------------------------
            "selling": {"vi": "Đang bán", "en": "Selling"},
            "sold": {"vi": "Đã bán", "en": "Sold"},
            "hidden": {"vi": "Tạm ẩn", "en": "Hidden"},
            "inactive": {"vi": "Ngừng bán", "en": "Inactive"},
            "available_date": {"vi": "Sắp mở bán", "en": "Available Soon"},

            # ---------------------------------------------------------------
            # 5. TransactionType - Loại giao dịch
            # ---------------------------------------------------------------
            "sale": {"vi": "Bán", "en": "Sale"},
            "rent": {"vi": "Cho thuê", "en": "Rent"},
            "transfer": {"vi": "Sang nhượng", "en": "Transfer"},

            # ---------------------------------------------------------------
            # 6. PropertyType - Loại hình bất động sản
            # ---------------------------------------------------------------
            "townhouse": {"vi": "Nhà phố", "en": "Townhouse"},
            "land_plot": {"vi": "Đất nền", "en": "Land Plot"},
            "apartment": {"vi": "Căn hộ", "en": "Apartment"},
            "condo": {"vi": "Chung cư", "en": "Condominium"},
            "street_front_house": {"vi": "Nhà mặt tiền", "en": "Street-Front House"},
            "villa": {"vi": "Biệt thự", "en": "Villa"},
            "hotel": {"vi": "Khách sạn", "en": "Hotel"},
            "business_premise": {"vi": "Mặt bằng kinh doanh", "en": "Business Premise"},
            "homestay": {"vi": "Homestay", "en": "Homestay"},

            # ---------------------------------------------------------------
            # 7. Orientation - Hướng bất động sản
            # ---------------------------------------------------------------
            "north": {"vi": "Bắc", "en": "North"},
            "northeast": {"vi": "Đông Bắc", "en": "Northeast"},
            "east": {"vi": "Đông", "en": "East"},
            "southeast": {"vi": "Đông Nam", "en": "Southeast"},
            "south": {"vi": "Nam", "en": "South"},
            "southwest": {"vi": "Tây Nam", "en": "Southwest"},
            "west": {"vi": "Tây", "en": "West"},
            "northwest": {"vi": "Tây Bắc", "en": "Northwest"},

            # ---------------------------------------------------------------
            # 8. PropertyCondition - Hiện trạng công trình
            # ---------------------------------------------------------------
            "new": {"vi": "Mới", "en": "New"},
            "used": {"vi": "Đã qua sử dụng", "en": "Used"},

            # ---------------------------------------------------------------
            # 9. VehicleType - Phương tiện tiếp cận / Lộ giới
            # ---------------------------------------------------------------
            "motorbike": {"vi": "Đường xe máy", "en": "Motorbike Access"},
            "car": {"vi": "Đường ô tô", "en": "Car Access"},
            "truck": {"vi": "Đường xe tải", "en": "Truck Access"},

            # ---------------------------------------------------------------
            # 10. RoadSurface - Loại bề mặt đường
            # ---------------------------------------------------------------
            "concrete": {"vi": "Đường bê tông", "en": "Concrete Road"},
            "asphalt": {"vi": "Đường nhựa", "en": "Asphalt Road"},
            "paved": {"vi": "Đường lát gạch/đá", "en": "Paved Road"},

            # ---------------------------------------------------------------
            # 11. RoadCondition - Độ dốc / địa hình đường
            # ---------------------------------------------------------------
            "flat": {"vi": "Bằng phẳng", "en": "Flat"},
            "sloped": {"vi": "Đường dốc", "en": "Sloped"},

            # ---------------------------------------------------------------
            # 12. ParkingType - Hình thức đỗ xe
            # ---------------------------------------------------------------
            "onsite": {"vi": "Chỗ đậu xe riêng (sân/gara)", "en": "Onsite Parking"},
            "nearby": {"vi": "Gần chỗ đậu xe công cộng", "en": "Nearby Parking"},
            "street": {"vi": "Đậu xe trên đường", "en": "Street Parking"},

            # ---------------------------------------------------------------
            # 13. OwnershipForm - Hình thức sở hữu
            # ---------------------------------------------------------------
            "private": {"vi": "Sở hữu riêng", "en": "Private Ownership"},
            "shared": {"vi": "Đồng sở hữu (Chung)", "en": "Shared Ownership"},
            "decentralized": {"vi": "Phân quyền", "en": "Decentralized Ownership"},

            # ---------------------------------------------------------------
            # 14. LandUseType - Mục đích sử dụng đất
            # ---------------------------------------------------------------
            "residential_land": {"vi": "Đất ở (Thổ cư)", "en": "Residential Land"},
            "commercial": {"vi": "Đất thương mại dịch vụ", "en": "Commercial Land"},
            "industrial": {"vi": "Đất công nghiệp", "en": "Industrial Land"},
            "agricultural": {"vi": "Đất nông nghiệp", "en": "Agricultural Land"},

            # ---------------------------------------------------------------
            # 15. TransactionMethod - Phương thức giao dịch
            # ---------------------------------------------------------------
            "notarized_contract": {"vi": "Hợp đồng công chứng", "en": "Notarized Contract"},
            "unnotarized_contract": {"vi": "Vi bằng / Giấy tay", "en": "Unnotarized / Bailiff Attested"},

            # ---------------------------------------------------------------
            # 16. FurnishedLevel - Mức độ bàn giao nội thất
            # ---------------------------------------------------------------
            "basic": {"vi": "Nội thất cơ bản", "en": "Basic Furnished"},
            "full": {"vi": "Đầy đủ nội thất", "en": "Fully Furnished"},

            # ---------------------------------------------------------------
            # 17. ProvinceType & DistrictType - Đơn vị hành chính
            # ---------------------------------------------------------------
            "lam_dong": {"vi": "Lâm Đồng", "en": "Lam Dong"},
            "da_lat": {"vi": "Đà Lạt", "en": "Da Lat"},

            # ---------------------------------------------------------------
            # 18. WardType - Phường / Xã tại Đà Lạt & Lạc Dương
            # ---------------------------------------------------------------
            "phuong_1_xuan_huong": {"vi": "Phường 1 (Xuân Hương)", "en": "Ward 1 (Xuan Huong)"},
            "phuong_2_xuan_huong": {"vi": "Phường 2 (Xuân Hương)", "en": "Ward 2 (Xuan Huong)"},
            "phuong_3_xuan_huong": {"vi": "Phường 3 (Xuân Hương)", "en": "Ward 3 (Xuan Huong)"},
            "phuong_4_xuan_huong": {"vi": "Phường 4 (Xuân Hương)", "en": "Ward 4 (Xuan Huong)"},
            "phuong_5_cam_ly": {"vi": "Phường 5 (Cam Ly)", "en": "Ward 5 (Cam Ly)"},
            "phuong_6_cam_ly": {"vi": "Phường 6 (Cam Ly)", "en": "Ward 6 (Cam Ly)"},
            "phuong_7_lang_biang": {"vi": "Phường 7 (Lang Biang)", "en": "Ward 7 (Lang Biang)"},
            "phuong_8_lam_vien": {"vi": "Phường 8 (Lâm Viên)", "en": "Ward 8 (Lam Vien)"},
            "phuong_9_lam_vien": {"vi": "Phường 9 (Lâm Viên)", "en": "Ward 9 (Lam Vien)"},
            "phuong_10_xuan_huong": {"vi": "Phường 10 (Xuân Hương)", "en": "Ward 10 (Xuan Huong)"},
            "phuong_11_xuan_truong": {"vi": "Phường 11 (Xuân Trường)", "en": "Ward 11 (Xuan Truong)"},
            "phuong_12_lam_vien": {"vi": "Phường 12 (Lâm Viên)", "en": "Ward 12 (Lam Vien)"},
            "xa_xuan_truong": {"vi": "Xã Xuân Trường", "en": "Xuan Truong Commune"},
            "xa_xuan_tho": {"vi": "Xã Xuân Thọ", "en": "Xuan Tho Commune"},
            "xa_ta_nung": {"vi": "Xã Tà Nung", "en": "Ta Nung Commune"},
            "xa_tram_hanh": {"vi": "Xã Trạm Hành", "en": "Tram Hanh Commune"},
            "thi_tran_lac_duong": {"vi": "Thị trấn Lạc Dương", "en": "Lac Duong Town"},

            # ---------------------------------------------------------------
            # 19. rentPaymentCycle - Kỳ hạn thanh toán tiền thuê
            # ---------------------------------------------------------------
            "monthly": {"vi": "Hàng tháng (1 tháng/lần)", "en": "Monthly"},
            "two_monthly": {"vi": "2 tháng / lần", "en": "Every 2 Months"},
            "quarterly": {"vi": "Hàng quý (3 tháng/lần)", "en": "Quarterly"},
            "semi_annually": {"vi": "Nửa năm (6 tháng/lần)", "en": "Semi-annually"},
            "annually": {"vi": "Hàng năm (1 năm/lần)", "en": "Annually"},
            "flexible": {"vi": "Thỏa thuận linh hoạt", "en": "Flexible Agreement"},

            # ---------------------------------------------------------------
            # 20. rentPurpose - Mục đích cho thuê
            # ---------------------------------------------------------------
            "residential": {"vi": "Để ở", "en": "Residential"},
            "office": {"vi": "Làm văn phòng", "en": "Office Space"},
            "warehouse": {"vi": "Kho xưởng", "en": "Warehouse"},
            "sublease": {"vi": "Cho phép thuê lại", "en": "Sublease Allowed"},

            # ---------------------------------------------------------------
            # 21. ElectricityCostType & WaterCostType - Chi phí điện nước
            # ---------------------------------------------------------------
            "state_rate": {"vi": "Giá nhà nước", "en": "State Rate"},
            "fixed_per_kwh": {"vi": "Giá cố định / kWh", "en": "Fixed per kWh"},
            "included": {"vi": "Đã bao gồm trong giá thuê", "en": "Included in Rent"},
            "per_m3": {"vi": "Tính theo m³", "en": "Per m³"},
            "per_person": {"vi": "Khoán theo đầu người", "en": "Per Person"},

            # ---------------------------------------------------------------
            # 22. PriceUnit - Đơn vị tính giá
            # ---------------------------------------------------------------
            "billion": {"vi": "Tỷ đồng", "en": "Billion VND"},
            "million": {"vi": "Triệu đồng", "en": "Million VND"},
            "million_per_month": {"vi": "Triệu/tháng", "en": "Million VND/month"},

            # ---------------------------------------------------------------
            # Qualified keys để xử lý xung đột giá trị giữa các Enum
            # ---------------------------------------------------------------
            "FurnishedLevel.none": {"vi": "Không có nội thất", "en": "Unfurnished"},
            "ParkingType.none": {"vi": "Không có chỗ đậu xe", "en": "No Parking"},
            "PendingAction.none": {"vi": "Không có", "en": "None"},
            "rentPurpose.residential": {"vi": "Để ở", "en": "Residential"},
            "LandUseType.residential_land": {"vi": "Đất ở (Thổ cư)", "en": "Residential Land"},
            "LandUseType.residential": {"vi": "Đất ở (Thổ cư)", "en": "Residential Land"},
            "rentPurpose.commercial": {"vi": "Mặt bằng kinh doanh", "en": "Commercial Space"},
            "LandUseType.commercial": {"vi": "Đất thương mại dịch vụ", "en": "Commercial Land"},
        }

        self._ui_translations: Dict[str, Dict[str, str]] = {
            "vi": {
                # Menu điều hướng
                "nav_home": "Trang chủ",
                "nav_my_properties": "Sản phẩm của tôi",
                "nav_post_property": "Đăng tin mới",
                "nav_approval_list": "Phê duyệt bài đăng",
                "nav_user_management": "Quản trị nhân sự",
                "nav_profile": "Hồ sơ cá nhân",
                "nav_logout": "Đăng xuất",
                "nav_login": "Đăng nhập",

                # Thông tin chung
                "app_title": "Hệ Thống Quản Lý Bất Động Sản Đà Lạt",
                "lbl_category": "Loại hình bất động sản",
                "lbl_transaction_type": "Loại giao dịch",
                "lbl_area": "Diện tích (m²)",
                "lbl_price": "Mức giá",
                "lbl_unit": "Đơn vị tính",
                "lbl_orientation": "Hướng bất động sản",
                "lbl_ownership": "Hình thức sở hữu",
                "lbl_land_use": "Mục đích sử dụng đất",
                "lbl_transaction_method": "Phương thức giao dịch",
                "lbl_vehicle_access": "Lộ giới / Tiếp cận",
                "lbl_furnished_level": "Nội thất",
                "lbl_structure": "Kết cấu (Số tầng)",
                "lbl_function": "Công năng",
                "lbl_description": "Mô tả chi tiết",
                "lbl_ward": "Phường / Xã",
                "lbl_street": "Tên đường",
                "lbl_status": "Trạng thái",
                "lbl_approval_status": "Trạng thái duyệt",
                "lbl_pending_action": "Hành động chờ",
            },
            "en": {
                # Menu navigation
                "nav_home": "Home",
                "nav_my_properties": "My Properties",
                "nav_post_property": "Post Property",
                "nav_approval_list": "Approval List",
                "nav_user_management": "User Management",
                "nav_profile": "Profile",
                "nav_logout": "Logout",
                "nav_login": "Login",

                # General labels
                "app_title": "Da Lat Real Estate Management System",
                "lbl_category": "Property Category",
                "lbl_transaction_type": "Transaction Type",
                "lbl_area": "Area (m²)",
                "lbl_price": "Price",
                "lbl_unit": "Price Unit",
                "lbl_orientation": "Orientation",
                "lbl_ownership": "Ownership Form",
                "lbl_land_use": "Land Use Type",
                "lbl_transaction_method": "Transaction Method",
                "lbl_vehicle_access": "Vehicle Access",
                "lbl_furnished_level": "Furnished Level",
                "lbl_structure": "Structure (Floors)",
                "lbl_function": "Function",
                "lbl_description": "Detailed Description",
                "lbl_ward": "Ward",
                "lbl_street": "Street",
                "lbl_status": "Status",
                "lbl_approval_status": "Approval Status",
                "lbl_pending_action": "Pending Action",
            },
        }


# Global convenience accessor instances
i18n = I18nManager.get_instance()
t = i18n.t
tr_enum = i18n.tr_enum
get_enum_label = i18n.tr_enum
get_enum_dict = i18n.get_enum_dict
get_enum_choices = i18n.get_enum_choices

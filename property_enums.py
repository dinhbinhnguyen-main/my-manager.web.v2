from enum import Enum


class UserRole(str, Enum):
    """
    Phân cấp vai trò người dùng trong hệ thống.
    """
    ADMIN = "admin"          # Quản trị viên tối cao: duyệt mọi bài, quản lý nhân sự
    MANAGER = "manager"      # Trưởng nhóm: duyệt bài các thành viên trong group_id
    MEMBER = "member"        # Nhân sự chính thức: tạo/sửa/xóa bài cá nhân (chờ duyệt)
    PROBATION = "probation"  # Nhân sự thử việc: tạo/sửa bài (chờ duyệt), cấm xóa bài
    UNKNOWN = "unknown"


class ApprovalStatus(str, Enum):
    """
    Trạng thái phê duyệt kiểm soát chất lượng.
    """
    DRAFT = "draft"          # Bản nháp chưa gửi duyệt
    PENDING = "pending"      # Đang chờ cấp quản lý phê duyệt
    APPROVED = "approved"    # Đã phê duyệt và đang hiển thị công khai
    REJECTED = "rejected"    # Bị từ chối (kèm lý do reject_reason)


class PendingAction(str, Enum):
    """
    Hành động đang chờ duyệt của sản phẩm.
    """
    NONE = "none"            # Không có hành động chờ
    CREATE = "create"        # Đề xuất tạo mới
    UPDATE = "update"        # Đề xuất cập nhật
    DELETE = "delete"        # Đề xuất xóa


class ProductStatus(str, Enum):
    """
    Trạng thái kinh doanh của sản phẩm.
    """

    SELLING = "selling"  # Đang bán
    SOLD = "sold"  # Đã bán
    HIDDEN = "hidden"  # Tạm ẩn / chưa công khai
    INACTIVE = "inactive"  # Đã ngừng bán
    AVAILABLE_DATE = "available_date"
    UNKNOWN = "unknown"  # Chưa xác định


# Giữ Status làm alias cho ProductStatus để đảm bảo tính tương thích
Status = ProductStatus


class TransactionType(str, Enum):
    """
    Loại giao dịch bất động sản.
    """

    SALE = "sale"  # Mua
    RENT = "rent"  # Thuê
    TRANSFER = "transfer"  # Sang nhượng / chuyển nhượng theo nghiệp vụ riêng
    UNKNOWN = "unknown"  # Chưa xác định


class PropertyType(str, Enum):
    """
    Loại hình bất động sản.
    """

    TOWNHOUSE = "townhouse"  # Nhà phố
    LAND_PLOT = "land_plot"  # Đất nền
    APARTMENT = "apartment"  # Căn hộ
    CONDO = "condo"  # Chung cư
    STREET_FRONT_HOUSE = "street_front_house"  # Mặt tiền
    VILLA = "villa"  # Biệt thự
    HOTEL = "hotel"  # Khách sạn
    BUSINESS_PREMISE = "business_premise"  # Mặt bằng kinh doanh
    HOMESTAY = "homestay"  # Homestay


class Orientation(str, Enum):
    """
    Hướng chính của bất động sản.
    """

    NORTH = "north"  # Bắc
    NORTHEAST = "northeast"  # Đông Bắc
    EAST = "east"  # Đông
    SOUTHEAST = "southeast"  # Đông Nam
    SOUTH = "south"  # Nam
    SOUTHWEST = "southwest"  # Tây Nam
    WEST = "west"  # Tây
    NORTHWEST = "northwest"  # Tây Bắc
    UNKNOWN = "unknown"  # Chưa xác định


class PropertyCondition(str, Enum):
    """
    Tình trạng hiện tại của bất động sản.
    """

    NEW = "new"  # Mới hoặc tình trạng gần như mới
    USED = "used"  # Đã qua sử dụng
    UNKNOWN = "unknown"  # Chưa xác định


class VehicleType(str, Enum):
    """
    Loại phương tiện có thể tiếp cận khu vực / đường vào bất động sản.
    """

    MOTORBIKE = "motorbike"  # Chủ yếu phù hợp với xe máy
    CAR = "car"  # Ô tô có thể tiếp cận
    TRUCK = "truck"  # Xe tải có thể tiếp cận
    UNKNOWN = "unknown"  # Chưa xác định


class RoadSurface(str, Enum):
    """
    Loại bề mặt đường tiếp cận bất động sản.
    """

    CONCRETE = "concrete"  # Đường bê tông
    ASPHALT = "asphalt"  # Đường nhựa
    PAVED = "paved"  # Đường lát gạch/đá
    UNKNOWN = "unknown"  # Chưa xác định


class RoadCondition(str, Enum):
    """
    Đặc điểm địa hình của đường tiếp cận bất động sản.
    """

    FLAT = "flat"  # Đường tương đối bằng phẳng
    SLOPED = "sloped"  # Đường có độ dốc
    UNKNOWN = "unknown"  # Chưa xác định


class ParkingType(str, Enum):
    """
    Hình thức đỗ xe của bất động sản.
    """

    ONSITE = "onsite"  # Chỗ đậu xe riêng (trong nhà, sân vườn)
    NEARBY = "nearby"  # Gần chỗ đậu xe (công cộng, vỉa hè)
    STREET = "street"  # Đậu xe trên đường
    NONE = "none"  # Không có chỗ đậu xe
    UNKNOWN = "unknown"  # Chưa xác định


class OwnershipForm(str, Enum):
    """
    Hình thức sở hữu bất động sản.
    """

    PRIVATE = "private"  # Sở hữu riêng
    SHARED = "shared"  # Đồng sở hữu / Chung
    DECENTRALIZED = "decentralized"  # Phân quyền
    UNKNOWN = "unknown"  # Chưa xác định


class LandUseType(str, Enum):
    """
    Mục đích sử dụng đất.
    """

    RESIDENTIAL = "residential"  # Đất ở
    COMMERCIAL = "commercial"  # Đất thương mại
    INDUSTRIAL = "industrial"  # Đất công nghiệp
    AGRICULTURAL = "agricultural"  # Đất nông nghiệp
    UNKNOWN = "unknown"  # Chưa xác định


class TransactionMethod(str, Enum):
    """
    Phương thức giao dịch.
    """

    NOTARIZED_CONTRACT = "notarized_contract"  # Hợp đồng công chứng
    UNNOTARIZED_CONTRACT = "unnotarized_contract"  # Vi bằng / Giấy tay
    UNKNOWN = "unknown"  # Chưa xác định


class FurnishedLevel(str, Enum):
    """
    Mức độ nội thất được bàn giao cùng bất động sản.
    """

    NONE = "none"  # Không có nội thất đáng kể.
    BASIC = "basic"  # Có nội thất cơ bản.
    FULL = "full"  # Đầy đủ nội thất.
    UNKNOWN = "unknown"  # Chưa xác định


class ProvinceType(str, Enum):
    LAM_DONG = "lam_dong"  # Lâm Đồng


class DistrictType(str, Enum):
    DA_LAT = "da_lat"  # Đà Lạt


class WardType(str, Enum):
    PHUONG_1 = "phuong_1_xuan_huong"  # Phường Xuân Hương
    PHUONG_2 = "phuong_2_xuan_huong"  # Phường Xuân Hương
    PHUONG_3 = "phuong_3_xuan_huong"  # Phường Xuân Hương
    PHUONG_4 = "phuong_4_xuan_huong"  # Phường Xuân Hương
    PHUONG_5 = "phuong_5_cam_ly"  # Phường Cam Ly
    PHUONG_6 = "phuong_6_cam_ly"  # Phường Cam Ly
    PHUONG_7 = "phuong_7_lang_biang"  # Phường Lang Biang
    PHUONG_8 = "phuong_8_lam_vien"  # Phường Lâm Viên
    PHUONG_9 = "phuong_9_lam_vien"  # Phường Lâm Viên
    PHUONG_10 = "phuong_10_xuan_huong"  # Phường Xuân Hương
    PHUONG_11 = "phuong_11_xuan_truong"  # Phường Xuân Trường
    PHUONG_12 = "phuong_12_lam_vien"  # Phường Lâm Viên
    XUAN_TRUONG = "xa_xuan_truong"  # Xã Xuân Trường
    XUAN_THO = "xa_xuan_tho"  # Xã Xuân Thọ
    TA_NUNG = "xa_ta_nung"  # Xã Tà Nung
    TRAM_HANH = "xa_tram_hanh"  # Xã Trạm Hành
    LAC_DUONG = "thi_tran_lac_duong"  # Thị trấn Lạc Dương


class rentPaymentCycle(str, Enum):
    """
    Kỳ hạn thanh toán tiền thuê.
    """

    MONTHLY = "monthly"  # Hàng tháng (1 tháng / lần)
    TWO_MONTHLY = "two_monthly"  # Hàng tháng (2 tháng / lần)
    QUARTERLY = "quarterly"  # Hàng quý (3 tháng / lần)
    SEMI_ANNUALLY = "semi_annually"  # Nửa năm (6 tháng / lần)
    ANNUALLY = "annually"  # Hàng năm (1 năm / lần)
    FLEXIBLE = "flexible"  # Linh hoạt / Thỏa thuận
    UNKNOWN = "unknown"  # Chưa xác định


class rentPurpose(str, Enum):
    """
    Mục đích cho thuê của bất động sản.
    """

    RESIDENTIAL = "residential"  # Để ở
    OFFICE = "office"  # Làm văn phòng
    COMMERCIAL = "commercial"  # Mặt bằng kinh doanh
    HOMESTAY = "homestay"  # Homestay / Căn hộ dịch vụ
    WAREHOUSE = "warehouse"  # Kho xưởng
    SUBLEASE = "sublease"  # Cho phép thuê lại
    UNKNOWN = "unknown"  # Chưa xác định


class ElectricityCostType(str, Enum):
    """
    Cách tính chi phí tiền điện.
    """

    STATE_RATE = "state_rate"  # Giá nhà nước
    FIXED_PER_KWH = "fixed_per_kwh"  # Giá cố định / kWh
    INCLUDED = "included"  # Đã bao gồm trong giá thuê
    UNKNOWN = "unknown"  # Chưa xác định


class WaterCostType(str, Enum):
    """
    Cách tính chi phí tiền nước.
    """

    STATE_RATE = "state_rate"  # Giá nhà nước
    PER_M3 = "per_m3"  # Tính theo m3
    PER_PERSON = "per_person"  # Khoán theo đầu người
    INCLUDED = "included"  # Đã bao gồm trong giá thuê
    UNKNOWN = "unknown"  # Chưa xác định

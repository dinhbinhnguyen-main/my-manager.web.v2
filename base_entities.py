import uuid
import datetime
from dataclasses import dataclass, asdict, field
from typing import Any, Dict, Type, TypeVar, Optional
from enum import Enum

from property_enums import (
    UserRole,
    ApprovalStatus,
    PendingAction,
    ProductStatus,
    TransactionType,
    ProvinceType,
    DistrictType,
    WardType,
    PropertyType,
)
from constants import (
    RealEstateProduct__Unit,
    RealEstateProduct__Legal,
    RealEstateProduct__BuildingLine,
    RealEstateProduct__Furniture,
)

T = TypeVar("T", bound="BaseEntity")


@dataclass
class BaseEntity:
    """
    Base class for all entities, providing unique identification and timestamp management.
    """

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(
        default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )
    updated_at: str = field(
        default_factory=lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

    def mark_created(self) -> None:
        """
        Initializes the unique ID and sets the initial creation and update timestamps.
        """
        if not self.id:
            self.id = str(uuid.uuid4())

        now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.created_at = now_str
        self.updated_at = now_str

    def touch(self) -> None:
        """
        Updates the 'updated_at' timestamp to the current local time.
        """
        self.updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the dataclass instance into a dictionary, ensuring Enum members are converted to values.
        """
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, Enum):
                data[key] = value.value
        return data

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> Optional[T]:
        """
        Creates an entity instance from a dictionary, filtering out keys that do not belong to the dataclass.
        """
        if not data:
            return None
        valid_keys = cls.__dataclass_fields__.keys()
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)


@dataclass
class UserEntity(BaseEntity):
    """
    Đại diện cho người dùng hệ thống (Admin, Manager, Member, Probation).
    """

    username: str = ""
    password_hash: str = ""
    role: UserRole = UserRole.MEMBER
    phone_number: str = ""
    logo_url: str = ""
    is_active: bool = False
    group_id: str = ""

    def __post_init__(self):
        if isinstance(self.role, str):
            try:
                self.role = UserRole(self.role.lower())
            except ValueError:
                self.role = UserRole.UNKNOWN
        if isinstance(self.is_active, (int, str)):
            if str(self.is_active).isdigit():
                self.is_active = bool(int(self.is_active))
            else:
                self.is_active = str(self.is_active).lower() in ("true", "1", "yes")


@dataclass
class PropertyEntity(BaseEntity):
    """
    Represents a real estate listing with detailed technical specifications and status.
    """

    pid: str = ""
    user_id: str = ""

    # --- Hệ thống kiểm duyệt ---
    approval_status: ApprovalStatus = ApprovalStatus.DRAFT
    pending_action: PendingAction = PendingAction.NONE
    reject_reason: str = ""

    # --- Thông tin sản phẩm ---
    title: str = ""
    image_url: str = ""
    status: ProductStatus = ProductStatus.HIDDEN
    transaction_type: TransactionType = TransactionType.SALE
    province: ProvinceType = ProvinceType.LAM_DONG
    district: DistrictType = DistrictType.DA_LAT
    ward: WardType = WardType.PHUONG_1
    street: str = ""
    category: PropertyType = PropertyType.TOWNHOUSE
    area: float = 0.0
    price: float = 0.0
    unit: RealEstateProduct__Unit = RealEstateProduct__Unit.BILLION
    legal: RealEstateProduct__Legal = RealEstateProduct__Legal.PRIVATE_CONSTRUCTION_DEED
    structure: float = 0.0
    function: str = ""
    building_line: RealEstateProduct__BuildingLine = (
        RealEstateProduct__BuildingLine.MOTORBIKE_ACCESS_ROAD
    )
    furniture: RealEstateProduct__Furniture = RealEstateProduct__Furniture.NO_FURNITURE
    description: str = ""

    def __post_init__(self):
        if not self.pid and self.id:
            self.pid = self.id

        try:
            self.area = float(self.area) if self.area else 0.0
        except (ValueError, TypeError):
            self.area = 0.0

        try:
            self.price = float(self.price) if self.price else 0.0
        except (ValueError, TypeError):
            self.price = 0.0

        try:
            self.structure = float(self.structure) if self.structure else 0.0
        except (ValueError, TypeError):
            self.structure = 0.0

        def parse_enum(value, enum_cls, default):
            if isinstance(value, str):
                try:
                    return enum_cls(value.lower())
                except ValueError:
                    return default
            return value

        # Parse Kiểm duyệt
        self.approval_status = parse_enum(
            self.approval_status, ApprovalStatus, ApprovalStatus.DRAFT
        )
        self.pending_action = parse_enum(
            self.pending_action, PendingAction, PendingAction.NONE
        )

        # Parse Thuộc tính BĐS
        self.status = parse_enum(self.status, ProductStatus, ProductStatus.HIDDEN)
        self.transaction_type = parse_enum(
            self.transaction_type, TransactionType, TransactionType.SALE
        )
        self.province = parse_enum(self.province, ProvinceType, ProvinceType.LAM_DONG)
        self.district = parse_enum(self.district, DistrictType, DistrictType.DA_LAT)
        self.ward = parse_enum(self.ward, WardType, WardType.PHUONG_1)
        self.category = parse_enum(self.category, PropertyType, PropertyType.TOWNHOUSE)
        self.unit = parse_enum(
            self.unit, RealEstateProduct__Unit, RealEstateProduct__Unit.BILLION
        )
        self.legal = parse_enum(
            self.legal,
            RealEstateProduct__Legal,
            RealEstateProduct__Legal.PRIVATE_CONSTRUCTION_DEED,
        )
        self.building_line = parse_enum(
            self.building_line,
            RealEstateProduct__BuildingLine,
            RealEstateProduct__BuildingLine.MOTORBIKE_ACCESS_ROAD,
        )
        self.furniture = parse_enum(
            self.furniture,
            RealEstateProduct__Furniture,
            RealEstateProduct__Furniture.NO_FURNITURE,
        )

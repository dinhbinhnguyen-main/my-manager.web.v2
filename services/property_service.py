import uuid
from typing import Dict, Any, List, Optional, Tuple
from base_entities import PropertyEntity, UserEntity
from property_enums import UserRole, ApprovalStatus, PendingAction, ProductStatus
from repositories.property_repository import PropertyRepository
from repositories.user_repository import UserRepository
from constants import DEFAULT_LOGO
from utils.i18n import tr_enum

# Giới hạn số lượng bài đăng tối đa cho nhân sự thử việc
PROBATION_MAX_PROPERTIES = 5

class PropertyService:
    def __init__(self):
        self.property_repo = PropertyRepository()
        self.user_repo = UserRepository()

    def get_public_listings(
        self,
        category: Optional[str] = None,
        transaction_type: Optional[str] = None,
        ward: Optional[str] = None,
        orientation: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        min_area: Optional[float] = None,
        max_area: Optional[float] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lấy danh sách BĐS đã duyệt hiển thị công khai.
        Tự động đính kèm thương hiệu cá nhân (author_logo, author_phone).
        """
        listings = self.property_repo.get_public_approved_list(
            category=category,
            transaction_type=transaction_type,
            ward=ward,
            orientation=orientation,
            min_price=min_price,
            max_price=max_price,
            min_area=min_area,
            max_area=max_area,
            search=search,
            sort_by=sort_by
        )
        for item in listings:
            if not item.get("author_logo"):
                item["author_logo"] = DEFAULT_LOGO
            if "title" not in item or not item["title"]:
                cat = tr_enum(item.get("category", ""))
                loc = item.get("street") or tr_enum(item.get("ward", ""))
                item["title"] = f"{cat} - {loc}" if loc else cat
            if "image_url" not in item and item.get("images"):
                try:
                    import json
                    imgs = json.loads(item["images"]) if isinstance(item["images"], str) else item["images"]
                    item["image_url"] = imgs[0] if imgs else ""
                except Exception:
                    item["image_url"] = ""
        return listings

    def get_public_detail(self, property_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy chi tiết một BĐS đã duyệt kèm thông tin liên hệ của nhân sự đăng bài.
        """
        detail = self.property_repo.get_public_approved_by_id(property_id)
        if detail:
            if not detail.get("author_logo"):
                detail["author_logo"] = DEFAULT_LOGO
            if "title" not in detail or not detail["title"]:
                cat = tr_enum(detail.get("category", ""))
                loc = detail.get("street") or tr_enum(detail.get("ward", ""))
                detail["title"] = f"{cat} - {loc}" if loc else cat
            if "image_url" not in detail and detail.get("images"):
                try:
                    import json
                    imgs = json.loads(detail["images"]) if isinstance(detail["images"], str) else detail["images"]
                    detail["image_url"] = imgs[0] if imgs else ""
                except Exception:
                    detail["image_url"] = ""
        return detail

    def get_user_properties(self, user_id: str) -> List[PropertyEntity]:
        """
        Lấy tất cả các bài đăng (cả approved, pending, rejected) của một nhân viên.
        """
        return self.property_repo.get_by_user_id(user_id)

    def create_property(
        self,
        user: UserEntity,
        form_data: Dict[str, Any],
        images: Optional[List[str]] = None
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Luồng Đăng mới BĐS:
        - ADMIN: Duyệt tự động ngay lập tức.
        - PROBATION: Kiểm tra giới hạn số lượng bài tối đa.
        - MEMBER / PROBATION: Tạo bản ghi approval_status = 'pending', pending_action = 'create'.
        """
        if user.role == UserRole.PROBATION:
            current_count = self.property_repo.count_by_user_id(user.id)
            if current_count >= PROBATION_MAX_PROPERTIES:
                return False, f"Nhân sự thử việc chỉ được đăng tối đa {PROBATION_MAX_PROPERTIES} bài đăng.", None

        new_id = str(uuid.uuid4())
        is_admin = (user.role == UserRole.ADMIN)

        prop = PropertyEntity(
            id=new_id,
            pid=new_id,
            user_id=user.id,
            approval_status=ApprovalStatus.APPROVED if is_admin else ApprovalStatus.PENDING,
            pending_action=PendingAction.NONE if is_admin else PendingAction.CREATE,
            reject_reason="",
            images=images or [],
            status=form_data.get("status", ProductStatus.SELLING if is_admin else ProductStatus.HIDDEN),
            transaction_type=form_data.get("transaction_type", "sale"),
            province=form_data.get("province", "lam_dong"),
            district=form_data.get("district", "da_lat"),
            ward=form_data.get("ward", "phuong_1_xuan_huong"),
            street=form_data.get("street", "").strip(),
            category=form_data.get("category", "townhouse"),
            area=form_data.get("area", 0.0),
            price=form_data.get("price", 0.0),
            unit=form_data.get("unit", "billion"),
            owner_name=form_data.get("owner_name", "").strip(),
            owner_phone=form_data.get("owner_phone", "").strip(),
            map_url=form_data.get("map_url", "").strip(),
            ownership=form_data.get("ownership", "private"),
            land_use=form_data.get("land_use", "residential_land"),
            transaction_method=form_data.get("transaction_method", "notarized_contract"),
            orientation=form_data.get("orientation", "unknown"),
            structure=form_data.get("structure", 0.0),
            function=form_data.get("function", "").strip(),
            vehicle_access=form_data.get("vehicle_access", "motorbike"),
            furnished_level=form_data.get("furnished_level", "none"),
            deposit=form_data.get("deposit", 0.0),
            payment_cycle=form_data.get("payment_cycle", "monthly"),
            rent_purpose=form_data.get("rent_purpose", "residential"),
            lease_term=form_data.get("lease_term", 12),
            electricity_cost=form_data.get("electricity_cost", "state_rate"),
            water_cost=form_data.get("water_cost", "state_rate"),
            description=form_data.get("description", "").strip()
        )

        self.property_repo.create(prop)
        if is_admin:
            msg = "Sản phẩm được tạo bởi Admin đã được duyệt và hiển thị công khai ngay lập tức."
        else:
            msg = "Tạo sản phẩm thành công! Đang chờ Quản lý duyệt trước khi hiển thị công khai."
        return True, msg, prop.id

    def update_property(
        self,
        user: UserEntity,
        prop_id: str,
        form_data: Dict[str, Any],
        images: Optional[List[str]] = None
    ) -> Tuple[bool, str]:
        """
        Luồng Chỉnh sửa BĐS:
        - Nếu bài đăng đã APPROVED:
          Giữ nguyên bài đang hoạt động ngoài trang chủ.
          Tạo một bản sao với pending_action = 'update' để Quản lý duyệt.
        - Nếu bài đăng đang PENDING hoặc REJECTED:
          Cho phép chỉnh sửa trực tiếp trên bản ghi đó và gửi lại duyệt.
        """
        prop = self.property_repo.get_by_id(prop_id)
        if not prop:
            return False, "Không tìm thấy bất động sản."

        # Kiểm tra quyền sở hữu
        if prop.user_id != user.id and user.role != UserRole.ADMIN:
            return False, "Bạn không có quyền chỉnh sửa bài đăng của người khác."

        # Nếu là Admin: cập nhật trực tiếp luôn
        if user.role == UserRole.ADMIN:
            self._apply_form_to_prop(prop, form_data, images)
            prop.approval_status = ApprovalStatus.APPROVED
            prop.pending_action = PendingAction.NONE
            prop.reject_reason = ""
            self.property_repo.update(prop)
            return True, "Admin đã cập nhật trực tiếp bài đăng thành công."

        # Nếu bài đang APPROVED: Tạo bản sao pending update (nếu chưa có bản sao nào)
        if prop.approval_status == ApprovalStatus.APPROVED:
            # Kiểm tra xem có bản sao pending update nào đang chờ duyệt cho pid này chưa
            existing_copies = [
                p for p in self.property_repo.get_by_pid(prop.pid)
                if p.approval_status == ApprovalStatus.PENDING and p.pending_action == PendingAction.UPDATE
            ]
            if existing_copies:
                draft = existing_copies[0]
                self._apply_form_to_prop(draft, form_data, images)
                self.property_repo.update(draft)
                return True, "Đã cập nhật lại bản nháp chờ duyệt."

            # Tạo bản sao mới
            new_draft_id = str(uuid.uuid4())
            draft = PropertyEntity(
                id=new_draft_id,
                pid=prop.pid,
                user_id=prop.user_id,
                approval_status=ApprovalStatus.PENDING,
                pending_action=PendingAction.UPDATE,
                reject_reason="",
                images=images if images is not None else prop.images,
                status=prop.status,
                transaction_type=form_data.get("transaction_type", prop.transaction_type),
                province=form_data.get("province", prop.province),
                district=form_data.get("district", prop.district),
                ward=form_data.get("ward", prop.ward),
                street=form_data.get("street", prop.street).strip(),
                category=form_data.get("category", prop.category),
                area=form_data.get("area", prop.area),
                price=form_data.get("price", prop.price),
                unit=form_data.get("unit", prop.unit),
                owner_name=form_data.get("owner_name", prop.owner_name).strip(),
                owner_phone=form_data.get("owner_phone", prop.owner_phone).strip(),
                map_url=form_data.get("map_url", prop.map_url).strip(),
                ownership=form_data.get("ownership", prop.ownership),
                land_use=form_data.get("land_use", prop.land_use),
                transaction_method=form_data.get("transaction_method", prop.transaction_method),
                orientation=form_data.get("orientation", prop.orientation),
                structure=form_data.get("structure", prop.structure),
                function=form_data.get("function", prop.function).strip(),
                vehicle_access=form_data.get("vehicle_access", prop.vehicle_access),
                deposit=form_data.get("deposit", prop.deposit),
                payment_cycle=form_data.get("payment_cycle", prop.payment_cycle),
                rent_purpose=form_data.get("rent_purpose", prop.rent_purpose),
                lease_term=form_data.get("lease_term", prop.lease_term),
                electricity_cost=form_data.get("electricity_cost", prop.electricity_cost),
                water_cost=form_data.get("water_cost", prop.water_cost),
                description=form_data.get("description", prop.description).strip()
            )
            self.property_repo.create(draft)
            return True, "Yêu cầu chỉnh sửa đã được tạo bản nháp và chuyển vào danh sách chờ Quản lý duyệt."

        # Nếu bài đang PENDING hoặc REJECTED: Cập nhật trực tiếp bản ghi nháp
        self._apply_form_to_prop(prop, form_data, images)
        prop.approval_status = ApprovalStatus.PENDING
        prop.pending_action = PendingAction.CREATE if prop.pending_action == PendingAction.CREATE else PendingAction.UPDATE
        prop.reject_reason = ""
        self.property_repo.update(prop)
        return True, "Đã cập nhật thông tin và gửi lại cho Quản lý phê duyệt."

    def delete_property(self, user: UserEntity, prop_id: str) -> Tuple[bool, str]:
        """
        Luồng Xóa BĐS:
        - PROBATION: Không được phép xóa.
        - ADMIN: Xóa hoặc chuyển trạng thái trực tiếp.
        - MEMBER:
          + Nếu là bản nháp chưa approved -> xóa thẳng.
          + Nếu là bản đã approved -> tạo yêu cầu xóa (pending_action = 'delete').
        """
        if user.role == UserRole.PROBATION:
            return False, "Nhân sự thử việc không được phép xóa bài đăng trong hệ thống."

        prop = self.property_repo.get_by_id(prop_id)
        if not prop:
            return False, "Không tìm thấy bất động sản."

        if prop.user_id != user.id and user.role != UserRole.ADMIN:
            return False, "Bạn không thể can thiệp vào dữ liệu của nhân sự khác."

        if user.role == UserRole.ADMIN:
            self.property_repo.delete(prop_id)
            return True, "Admin đã xóa bài đăng thành công."

        # Nếu bài chưa từng được duyệt (draft / pending / rejected): Xóa thẳng
        if prop.approval_status != ApprovalStatus.APPROVED:
            self.property_repo.delete(prop_id)
            return True, "Đã xóa bản nháp thành công."

        # Nếu bài đang approved: gửi yêu cầu chờ duyệt xóa
        prop.approval_status = ApprovalStatus.PENDING
        prop.pending_action = PendingAction.DELETE
        self.property_repo.update(prop)
        return True, "Yêu cầu xóa bài đăng đã được chuyển đến cấp Quản lý phê duyệt."

    def get_pending_list_for_reviewer(self, reviewer: UserEntity) -> List[Dict[str, Any]]:
        """
        Lấy danh sách các bài đăng đang chờ duyệt.
        - ADMIN: Xem toàn bộ bài đăng chờ duyệt của toàn sàn.
        - MANAGER: Chỉ xem các bài đăng của các Member thuộc group_id của mình.
        """
        if reviewer.role == UserRole.ADMIN:
            items = self.property_repo.get_pending_approvals(group_id=None)
        elif reviewer.role == UserRole.MANAGER:
            if not reviewer.group_id:
                return []
            items = self.property_repo.get_pending_approvals(group_id=reviewer.group_id)
        else:
            return []

        for item in items:
            if "title" not in item or not item["title"]:
                cat = tr_enum(item.get("category", ""))
                loc = item.get("street") or tr_enum(item.get("ward", ""))
                item["title"] = f"{cat} - {loc}" if loc else cat
        return items

    def get_comparison_data(self, pending_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy dữ liệu để đối chiếu giữa bản nháp mới và bản gốc đang approved (dành cho yêu cầu UPDATE).
        """
        pending = self.property_repo.get_by_id(pending_id)
        if not pending:
            return None

        original = None
        if pending.pending_action == PendingAction.UPDATE:
            # Tìm bản ghi approved có cùng pid
            all_by_pid = self.property_repo.get_by_pid(pending.pid)
            for p in all_by_pid:
                if p.id != pending.id and p.approval_status == ApprovalStatus.APPROVED:
                    original = p
                    break

        author = self.user_repo.get_by_id(pending.user_id)
        return {
            "pending": pending,
            "original": original,
            "author": author
        }

    def approve(self, reviewer: UserEntity, pending_id: str) -> Tuple[bool, str]:
        """
        Phê duyệt yêu cầu (Create / Update / Delete)
        """
        pending = self.property_repo.get_by_id(pending_id)
        if not pending:
            return False, "Không tìm thấy yêu cầu cần duyệt."

        # Kiểm tra thẩm quyền duyệt
        if not self._can_review(reviewer, pending.user_id):
            return False, "Bạn không có thẩm quyền phê duyệt yêu cầu này."

        if pending.pending_action == PendingAction.CREATE:
            pending.approval_status = ApprovalStatus.APPROVED
            pending.pending_action = PendingAction.NONE
            pending.status = ProductStatus.SELLING
            pending.reject_reason = ""
            self.property_repo.update(pending)
            return True, f"Đã duyệt tạo mới bài đăng '{pending.display_title}'."

        elif pending.pending_action == PendingAction.UPDATE:
            # Tìm bản ghi gốc đang approved
            all_by_pid = self.property_repo.get_by_pid(pending.pid)
            original = None
            for p in all_by_pid:
                if p.id != pending.id and p.approval_status == ApprovalStatus.APPROVED:
                    original = p
                    break

            if original:
                # Đè dữ liệu mới từ pending vào original
                self._copy_data(source=pending, target=original)
                original.approval_status = ApprovalStatus.APPROVED
                original.pending_action = PendingAction.NONE
                original.reject_reason = ""
                self.property_repo.update(original)
                # Dọn dẹp bản nháp
                self.property_repo.delete(pending.id)
                return True, f"Đã duyệt cập nhật dữ liệu cho bài đăng '{original.display_title}'."
            else:
                # Nếu không tìm thấy bài gốc, thăng hạng bản nháp thành bài chính
                pending.approval_status = ApprovalStatus.APPROVED
                pending.pending_action = PendingAction.NONE
                self.property_repo.update(pending)
                return True, "Đã duyệt và áp dụng thay đổi."

        elif pending.pending_action == PendingAction.DELETE:
            # Chuyển trạng thái sang INACTIVE hoặc xóa khỏi sàn
            pending.status = ProductStatus.INACTIVE
            pending.approval_status = ApprovalStatus.APPROVED
            pending.pending_action = PendingAction.NONE
            self.property_repo.update(pending)
            return True, f"Đã phê duyệt xóa bài đăng '{pending.display_title}' (chuyển sang trạng thái ngừng bán)."

        return False, "Hành động chờ không xác định."

    def reject(self, reviewer: UserEntity, pending_id: str, reason: str) -> Tuple[bool, str]:
        """
        Từ chối yêu cầu kèm lý do để nhân viên chỉnh sửa lại.
        """
        pending = self.property_repo.get_by_id(pending_id)
        if not pending:
            return False, "Không tìm thấy yêu cầu cần xử lý."

        if not self._can_review(reviewer, pending.user_id):
            return False, "Bạn không có thẩm quyền từ chối yêu cầu này."

        reason = reason.strip() or "Nội dung hoặc hình ảnh chưa đạt tiêu chuẩn quy định sàn."
        pending.approval_status = ApprovalStatus.REJECTED
        pending.reject_reason = reason
        self.property_repo.update(pending)
        return True, "Đã từ chối yêu cầu và gửi phản hồi lý do cho nhân viên."

    def _can_review(self, reviewer: UserEntity, author_id: str) -> bool:
        if reviewer.role == UserRole.ADMIN:
            return True
        if reviewer.role == UserRole.MANAGER:
            author = self.user_repo.get_by_id(author_id)
            if author and author.group_id and reviewer.group_id:
                return author.group_id == reviewer.group_id
        return False

    def _apply_form_to_prop(self, prop: PropertyEntity, form_data: Dict[str, Any], images: Optional[List[str]]):
        if images is not None:
            prop.images = images

        prop.status = form_data.get("status", prop.status)
        prop.transaction_type = form_data.get("transaction_type", prop.transaction_type)
        prop.province = form_data.get("province", prop.province)
        prop.district = form_data.get("district", prop.district)
        prop.ward = form_data.get("ward", prop.ward)
        prop.street = form_data.get("street", prop.street).strip()
        prop.category = form_data.get("category", prop.category)
        prop.area = form_data.get("area", prop.area)
        prop.price = form_data.get("price", prop.price)
        prop.unit = form_data.get("unit", prop.unit)
        prop.owner_name = form_data.get("owner_name", prop.owner_name).strip()
        prop.owner_phone = form_data.get("owner_phone", prop.owner_phone).strip()
        prop.map_url = form_data.get("map_url", prop.map_url).strip()
        prop.ownership = form_data.get("ownership", prop.ownership)
        prop.land_use = form_data.get("land_use", prop.land_use)
        prop.transaction_method = form_data.get("transaction_method", prop.transaction_method)
        prop.orientation = form_data.get("orientation", prop.orientation)
        prop.structure = form_data.get("structure", prop.structure)
        prop.function = form_data.get("function", prop.function).strip()
        prop.vehicle_access = form_data.get("vehicle_access", prop.vehicle_access)
        prop.furnished_level = form_data.get("furnished_level", prop.furnished_level)
        prop.deposit = form_data.get("deposit", prop.deposit)
        prop.payment_cycle = form_data.get("payment_cycle", prop.payment_cycle)
        prop.rent_purpose = form_data.get("rent_purpose", prop.rent_purpose)
        prop.lease_term = form_data.get("lease_term", prop.lease_term)
        prop.electricity_cost = form_data.get("electricity_cost", prop.electricity_cost)
        prop.water_cost = form_data.get("water_cost", prop.water_cost)
        prop.description = form_data.get("description", prop.description).strip()

    def _copy_data(self, source: PropertyEntity, target: PropertyEntity):
        target.images = source.images[:]
        target.status = source.status
        target.transaction_type = source.transaction_type
        target.province = source.province
        target.district = source.district
        target.ward = source.ward
        target.street = source.street
        target.category = source.category
        target.area = source.area
        target.price = source.price
        target.unit = source.unit
        target.owner_name = source.owner_name
        target.owner_phone = source.owner_phone
        target.map_url = source.map_url
        target.ownership = source.ownership
        target.land_use = source.land_use
        target.transaction_method = source.transaction_method
        target.orientation = source.orientation
        target.structure = source.structure
        target.function = source.function
        target.vehicle_access = source.vehicle_access
        target.furnished_level = source.furnished_level
        target.deposit = source.deposit
        target.payment_cycle = source.payment_cycle
        target.rent_purpose = source.rent_purpose
        target.lease_term = source.lease_term
        target.electricity_cost = source.electricity_cost
        target.water_cost = source.water_cost
        target.description = source.description

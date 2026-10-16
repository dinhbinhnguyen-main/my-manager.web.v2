import os
import unittest
from base_entities import UserEntity, PropertyEntity
from property_enums import UserRole, ApprovalStatus, PendingAction, ProductStatus
from services.auth_service import AuthService
from services.user_service import UserService
from services.property_service import PropertyService
from repositories.database import init_db

class TestRealEstateWorkflow(unittest.TestCase):
    def setUp(self):
        init_db()
        self.auth_svc = AuthService()
        self.user_svc = UserService()
        self.prop_svc = PropertyService()

    def test_01_registration_and_admin_activation_workflow(self):
        """
        Luồng Đăng ký:
        Nhân sự điền form tạo tài khoản -> is_active = False ->
        Admin kiểm tra danh sách và bật is_active = True -> Nhân sự đăng nhập thành công.
        """
        import uuid
        username = f"test_staff_{uuid.uuid4().hex[:6]}"
        pwd = "securepassword123"
        
        # 1. Đăng ký
        success, msg = self.auth_svc.register(
            username=username,
            password=pwd,
            phone_number="0911222333",
            role_str="member",
            group_id="GROUP_TEST"
        )
        self.assertTrue(success)
        
        # 2. Thử đăng nhập khi chưa kích hoạt
        user, login_msg = self.auth_svc.authenticate(username, pwd)
        self.assertIsNone(user)
        self.assertIn("CHƯA được Admin kích hoạt", login_msg)

        # 3. Admin kích hoạt
        inactive_user = self.auth_svc.user_repo.get_by_username(username)
        self.assertFalse(inactive_user.is_active)
        toggle_success, toggle_msg = self.user_svc.toggle_user_active(inactive_user.id)
        self.assertTrue(toggle_success)

        # 4. Đăng nhập lại sau khi Admin kích hoạt
        activated_user, login_ok_msg = self.auth_svc.authenticate(username, pwd)
        self.assertIsNotNone(activated_user)
        self.assertTrue(activated_user.is_active)
        print("✓ Test 01: Quy trình Đăng ký -> Chờ duyệt -> Admin kích hoạt -> Đăng nhập PASSED")

    def test_02_lead_protection_on_public_listings(self):
        """
        Luồng Xem (READ) & Cá nhân hóa:
        Trang chủ chỉ hiển thị approved, tự động đính kèm logo và SĐT người đăng.
        """
        public_items = self.prop_svc.get_public_listings()
        self.assertGreater(len(public_items), 0)
        for item in public_items:
            self.assertEqual(item["approval_status"], "approved")
            self.assertIn("author_phone", item)
            self.assertIn("author_logo", item)
            self.assertTrue(len(item["author_phone"]) > 0)
        print("✓ Test 02: Luồng Xem & Cá nhân hóa hotline/logo người đăng PASSED")

    def test_03_property_creation_approval_flow(self):
        """
        Luồng Đề xuất Tạo mới:
        - Member tạo: approval_status = 'pending', pending_action = 'create'
        - Admin tạo: duyệt ngay lập tức (approved, none)
        """
        admin = self.auth_svc.user_repo.get_by_username("admin")
        member = self.auth_svc.user_repo.get_by_username("member_an")

        # Member tạo bài mới
        form_data = {
            "title": "Nhà vườn đèo Prenn view rừng thông",
            "category": "townhouse",
            "transaction_type": "sale",
            "ward": "phuong_3_xuan_huong",
            "area": "150.0",
            "price": "6.5",
            "unit": "billion",
            "legal": "private_construction_deed"
        }
        ok, msg, prop_id = self.prop_svc.create_property(member, form_data)
        self.assertTrue(ok)
        created_prop = self.prop_svc.property_repo.get_by_id(prop_id)
        self.assertEqual(created_prop.approval_status, ApprovalStatus.PENDING)
        self.assertEqual(created_prop.pending_action, PendingAction.CREATE)

        # Admin tạo bài mới
        admin_ok, admin_msg, admin_prop_id = self.prop_svc.create_property(admin, form_data)
        self.assertTrue(admin_ok)
        admin_prop = self.prop_svc.property_repo.get_by_id(admin_prop_id)
        self.assertEqual(admin_prop.approval_status, ApprovalStatus.APPROVED)
        self.assertEqual(admin_prop.pending_action, PendingAction.NONE)
        print("✓ Test 03: Đề xuất Tạo mới (Member chờ duyệt, Admin duyệt ngay) PASSED")

    def test_04_update_clone_and_approval_workflow(self):
        """
        Luồng Chỉnh sửa (UPDATE):
        Giữ nguyên bản ghi đang hoạt động, tạo bản nháp pending_action = 'update' cùng pid.
        Khi Manager duyệt: ghi đè bản mới vào bài gốc và xóa bản nháp.
        """
        manager = self.auth_svc.user_repo.get_by_username("manager_lamvien")
        member = self.auth_svc.user_repo.get_by_username("member_an")

        # Lấy 1 bài đã approved của member_an
        props = [p for p in self.prop_svc.get_user_properties(member.id) if p.approval_status == ApprovalStatus.APPROVED]
        self.assertTrue(len(props) > 0)
        original = props[0]
        original_price = original.price

        # Member gửi yêu cầu chỉnh sửa giá và tiêu đề
        update_data = {
            "title": original.title + " [GIẢM GIÁ ĐẶC BIỆT]",
            "price": original_price - 1.0,
            "area": original.area,
            "category": original.category.value,
            "transaction_type": original.transaction_type.value,
            "ward": original.ward.value,
            "unit": original.unit.value,
            "legal": original.legal.value
        }
        update_ok, update_msg = self.prop_svc.update_property(member, original.id, update_data)
        self.assertTrue(update_ok)

        # Kiểm tra: Bản ghi gốc trên sàn VẪN GIỮ NGUYÊN
        unmodified_original = self.prop_svc.property_repo.get_by_id(original.id)
        self.assertEqual(unmodified_original.price, original_price)
        self.assertEqual(unmodified_original.approval_status, ApprovalStatus.APPROVED)

        # Kiểm tra: Có bản nháp pending update được sinh ra với cùng pid
        copies = self.prop_svc.property_repo.get_by_pid(original.pid)
        draft = next(c for c in copies if c.id != original.id)
        self.assertEqual(draft.approval_status, ApprovalStatus.PENDING)
        self.assertEqual(draft.pending_action, PendingAction.UPDATE)
        self.assertEqual(draft.price, original_price - 1.0)

        # Manager duyệt yêu cầu
        approve_ok, approve_msg = self.prop_svc.approve(manager, draft.id)
        self.assertTrue(approve_ok)

        # Sau khi duyệt: Bản ghi gốc đã được cập nhật giá mới, bản nháp bị xóa
        updated_original = self.prop_svc.property_repo.get_by_id(original.id)
        self.assertEqual(updated_original.price, original_price - 1.0)
        self.assertIn("[GIẢM GIÁ ĐẶC BIỆT]", updated_original.title)
        self.assertIsNone(self.prop_svc.property_repo.get_by_id(draft.id))
        print("✓ Test 04: Luồng Sửa đổi (Tạo bản nháp giữ nguyên bài gốc -> Manager duyệt) PASSED")

    def test_05_probation_restrictions(self):
        """
        Quyền hạn PROBATION (Thử việc): Bị cấm xóa bài đăng.
        """
        probation_user = self.auth_svc.user_repo.get_by_username("probation_binh")
        
        # Tạo thử 1 bài cho probation
        form_data = {
            "title": "Nhà cấp 4 Phường 7",
            "category": "townhouse",
            "price": "3.5",
            "area": "80"
        }
        self.prop_svc.create_property(probation_user, form_data)
        user_props = self.prop_svc.get_user_properties(probation_user.id)
        self.assertTrue(len(user_props) > 0)
        prop_id = user_props[0].id

        # Thử xóa bài
        del_ok, del_msg = self.prop_svc.delete_property(probation_user, prop_id)
        self.assertFalse(del_ok)
        self.assertIn("Nhân sự thử việc không được phép xóa", del_msg)
        print("✓ Test 05: Giới hạn Phân quyền PROBATION (Chặn xóa bài) PASSED")

if __name__ == "__main__":
    unittest.main()

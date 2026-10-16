# Hệ Thống Quản Lý Bất Động Sản Nội Bộ (Real Estate Internal Management)

Hệ thống được thiết kế theo kiến trúc 3 lớp chuẩn Python/Flask kết hợp cơ sở dữ liệu SQLite, đáp ứng mô hình **phân cấp 4 cấp bậc người dùng (User Hierarchy)**, **luồng phê duyệt kiểm soát chất lượng nghiêm ngặt (Approval Workflow Engine)** và **bảo vệ quyền lợi khai thác kinh doanh của từng chuyên viên (Lead Protection)**.

---

## 1. Cấu Trúc Dự Án (3-Tier Layered Architecture)

```text
my-manager.web.v2/
├── app.py                      # Khởi chạy Flask App, nạp context & template filters
├── config.py                   # Cấu hình môi trường (Secret Key, DB Path, Uploads)
├── constants.py                # Hằng số hệ thống, đường dẫn cấu hình
├── property_enums.py           # Enums: UserRole, ApprovalStatus, PendingAction, BĐS enums
├── base_entities.py            # BaseEntity, UserEntity, PropertyEntity (Dataclasses)
├── template_filters.py         # Bộ lọc Jinja2 hiển thị nhãn Tiếng Việt & badge trạng thái
│
├── repositories/               # [TẦNG 1: DATABASE & SQL THUẦN]
│   ├── database.py             # SQLite context manager, PRAGMA foreign_keys, WAL mode
│   ├── user_repository.py      # Truy vấn bảng `users` bằng SQL thuần có tham số
│   └── property_repository.py  # Truy vấn bảng `properties` (Filter pending, approved, join author)
│
├── services/                   # [TẦNG 2: NÃO BỘ NGHIỆP VỤ & PHÂN QUYỀN RBAC]
│   ├── auth_service.py         # Hash mật khẩu, xác thực, đăng ký chờ duyệt (is_active=False)
│   ├── user_service.py         # Kích hoạt nhân sự, gán group_id, đổi role
│   ├── property_service.py     # Luồng Tạo/Sửa/Xóa nháp, Phê duyệt, Kiểm soát quyền Probation
│   └── security.py             # Decorators: @login_required, @roles_required
│
├── routes/                     # [TẦNG ĐIỀU HƯỚNG / FLASK BLUEPRINTS]
│   ├── auth_routes.py          # /login, /register, /logout, /profile
│   ├── public_routes.py        # / (Trang chủ BĐS đã approved), /property/<id> (Chi tiết & Hotline)
│   ├── member_routes.py        # /dashboard/properties (BĐS cá nhân, tạo mới, đề xuất sửa/xóa)
│   ├── manager_routes.py       # /dashboard/manager/approvals, /diff (Duyệt theo group_id)
│   └── admin_routes.py         # /dashboard/admin/users, /all-approvals (Quản trị toàn sàn)
│
├── templates/                  # [TẦNG 3: GIAO DIỆN JINJA2]
│   ├── base.html               # Master layout (Navbar thích ứng UserRole, thông báo Flash)
│   ├── auth/                   # login.html, register.html, profile.html
│   ├── public/                 # index.html, detail.html (Thẻ BĐS đính kèm hotline/logo)
│   ├── member/                 # my_properties.html, property_form.html
│   ├── manager/                # approval_list.html, review_diff.html (Đối chiếu 2 cột dữ liệu)
│   └── admin/                  # user_management.html (Kích hoạt is_active & phân quyền)
│
├── static/
│   ├── css/styles.css          # Giao diện responsive hiện đại, bảng so sánh diff, thẻ BĐS
│   └── uploads/                # Lưu trữ logo người dùng & ảnh sản phẩm
├── seed_data.py                # Script tạo tài khoản mẫu và dữ liệu khởi tạo
└── test_workflow.py            # Test suite tự động kiểm thử toàn bộ 5 luồng nghiệp vụ
```

---

## 2. Tài Khoản Khởi Tạo Mẫu Để Kiểm Thử

Hệ thống đã có sẵn dữ liệu mẫu (chạy lại bằng `python3 seed_data.py` nếu cần):

| Tài khoản | Mật khẩu | Vai trò | Nhóm (group_id) | Trạng thái | Ghi chú quyền hạn |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **admin** | `admin123` | `ADMIN` | `GROUP_HQ` | Active | Toàn quyền, duyệt mọi bài, kích hoạt user. Bài đăng tự duyệt ngay. |
| **manager_lamvien** | `password123` | `MANAGER` | `GROUP_LAMVIEN` | Active | Trưởng nhóm, xem và duyệt bài của các thành viên cùng nhóm. |
| **member_an** | `password123` | `MEMBER` | `GROUP_LAMVIEN` | Active | Nhân sự chính thức, tạo/sửa/xóa bài cá nhân (chờ duyệt). |
| **probation_binh** | `password123` | `PROBATION` | `GROUP_LAMVIEN` | Active | Thử việc, tối đa 5 bài, **bị cấm tuyệt đối quyền xóa bài**. |
| **ung_vien_moi** | `password123` | `MEMBER` | `GROUP_LAMVIEN` | Inactive | Tài khoản mới đăng ký, **chờ Admin bật `is_active = True`**. |

---

## 3. Các Luồng Hoạt Động Cốt Lõi (Core Workflows)

### 3.1. Luồng Đăng ký & Kích hoạt nhân sự
1. Người dùng vào `/register` đăng ký thông tin (`username`, `password`, `phone_number`, `role`, `group_id`).
2. Tài khoản tự động được lưu với `is_active = False`. Người dùng chưa thể đăng nhập.
3. Quản trị viên (`admin`) đăng nhập vào `/dashboard/admin/users`, thấy tài khoản trong danh sách và bấm **"Kích hoạt"** (`is_active = True`).
4. Nhân viên đăng nhập thành công.

### 3.2. Luồng Cá nhân hóa kinh doanh (Lead Protection)
- Khách hàng xem danh sách trang chủ `/` hoặc chi tiết `/property/<id>`.
- Hệ thống thực hiện `JOIN properties` với `users` theo `user_id`.
- Thẻ sản phẩm và trang chi tiết **tự động hiển thị Logo, Tên và Số điện thoại** của chính chuyên viên đăng bài, kèm nút **"Gọi ngay"** và **"Nhắn tin Zalo"** trực tiếp đến đầu chủ đó.

### 3.3. Luồng Đề xuất & Kiểm duyệt (Version Tracking Engine)
- **Tạo mới**: Tạo bản ghi với `approval_status = 'pending'`, `pending_action = 'create'`.
- **Chỉnh sửa**: Nếu bài đang `approved` ngoài trang chủ:
  - Bài gốc **vẫn giữ nguyên** để khách hàng tiếp tục xem.
  - Hệ thống tạo một bản sao với cùng `pid`, mang trạng thái `approval_status = 'pending'`, `pending_action = 'update'`.
  - Quản lý vào `/dashboard/manager/approvals/<id>/diff` để xem **bảng đối chiếu 2 cột** (Cột trái: bài đang bán; Cột phải: bài đề xuất mới).
  - Bấm **"Duyệt"**: Hệ thống ghi đè dữ liệu mới vào bài gốc và xóa bản nháp.
  - Bấm **"Từ chối"**: Hệ thống lưu `reject_reason` để nhân viên chỉnh sửa lại.
- **Xóa**: Tạo đề xuất `pending_action = 'delete'` để Quản lý duyệt. Nhân sự thử việc (Probation) sẽ bị hệ thống chặn xóa.

---

## 4. Hướng Dẫn Chạy Ứng Dụng

### Khởi chạy Server:
```bash
python3 app.py
```
Ứng dụng sẽ hoạt động tại địa chỉ: `http://127.0.0.1:5001/`

### Chạy Bộ Kiểm Thử Tự Động (Unit & Integration Tests):
```bash
python3 test_workflow.py
```
Tất cả 5 kịch bản kiểm thử (Đăng ký, Duyệt kích hoạt, Lead Protection, Bản sao Update Diff, Chặn xóa Probation) sẽ được kiểm tra tự động.

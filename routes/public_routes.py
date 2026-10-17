from flask import Blueprint, render_template, request, abort
from services.property_service import PropertyService
from property_enums import (
    PropertyType,
    TransactionType,
    WardType,
    ProvinceType,
    DistrictType,
    Orientation
)

public_bp = Blueprint("public", __name__)
property_service = PropertyService()

@public_bp.route("/")
def index():
    category = request.args.get("category")
    transaction_type = request.args.get("transaction_type")
    ward = request.args.get("ward")
    orientation = request.args.get("orientation")
    search = request.args.get("search")
    sort_by = request.args.get("sort_by", "newest")

    def parse_float(val):
        if not val:
            return None
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    min_price = parse_float(request.args.get("min_price"))
    max_price = parse_float(request.args.get("max_price"))
    min_area = parse_float(request.args.get("min_area"))
    max_area = parse_float(request.args.get("max_area"))

    properties = property_service.get_public_listings(
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

    categories = list(PropertyType)
    transaction_types = list(TransactionType)
    wards = list(WardType)
    orientations = [o for o in Orientation if o != Orientation.UNKNOWN]

    return render_template(
        "public/index.html",
        properties=properties,
        categories=categories,
        transaction_types=transaction_types,
        wards=wards,
        orientations=orientations,
        current_category=category,
        current_transaction_type=transaction_type,
        current_ward=ward,
        current_orientation=orientation,
        current_min_price=request.args.get("min_price", ""),
        current_max_price=request.args.get("max_price", ""),
        current_min_area=request.args.get("min_area", ""),
        current_max_area=request.args.get("max_area", ""),
        current_sort_by=sort_by,
        search_query=search or ""
    )

@public_bp.route("/property/<property_id>")
def property_detail(property_id: str):
    property_item = property_service.get_public_detail(property_id)
    if not property_item:
        abort(404, description="Sản phẩm không tồn tại hoặc chưa được phê duyệt.")

    return render_template("public/detail.html", property=property_item)

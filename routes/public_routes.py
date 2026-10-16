from flask import Blueprint, render_template, request, abort
from services.property_service import PropertyService
from property_enums import (
    PropertyType,
    TransactionType,
    WardType,
    ProvinceType,
    DistrictType
)

public_bp = Blueprint("public", __name__)
property_service = PropertyService()

@public_bp.route("/")
def index():
    category = request.args.get("category")
    transaction_type = request.args.get("transaction_type")
    ward = request.args.get("ward")
    search = request.args.get("search")

    properties = property_service.get_public_listings(
        category=category,
        transaction_type=transaction_type,
        ward=ward,
        search=search
    )

    categories = list(PropertyType)
    transaction_types = list(TransactionType)
    wards = list(WardType)

    return render_template(
        "public/index.html",
        properties=properties,
        categories=categories,
        transaction_types=transaction_types,
        wards=wards,
        current_category=category,
        current_transaction_type=transaction_type,
        current_ward=ward,
        search_query=search or ""
    )

@public_bp.route("/property/<property_id>")
def property_detail(property_id: str):
    property_item = property_service.get_public_detail(property_id)
    if not property_item:
        abort(404, description="Sản phẩm không tồn tại hoặc chưa được phê duyệt.")

    return render_template("public/detail.html", property=property_item)

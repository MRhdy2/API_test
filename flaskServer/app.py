"""Local backend used by the API automation examples.

The bundled ``flaskServer.exe`` targets Windows and cannot run on macOS.  This
module provides the same sample endpoints natively so the project's API tests
can be executed locally and deterministically.
"""

from itertools import count
from threading import Lock

from flask import Flask, jsonify, request


app = Flask(__name__)

_order_ids = count(202609230001)
_logistics_order_ids = count(202609230001)
_schedule_ids = count(202609230001)
_reconciliation_ids = count(202609230001)
_carrier_ids = count(202609230001)
_state_lock = Lock()
_orders = {}
_logistics_orders = {}
_schedules = {}
_carriers = {}
_cart = {}

LOGISTICS_SESSION = "local-logistics-session"


def request_data():
    """Return JSON, form, or query input using its natural Python shape."""
    if request.is_json:
        return request.get_json(silent=True) or {}
    if request.form:
        return request.form.to_dict()
    return request.args.to_dict()


@app.get("/health")
def health():
    return jsonify(status="ok", service="pythonproject-local-api")


@app.post("/dar/user/login")
def login():
    data = request_data()
    if data.get("user_name") == "test01" and data.get("passwd") == "admin123":
        response = jsonify(
            error_code=None,
            msg="登录成功",
            msg_code=200,
            token="local-test-token",
        )
        response.set_cookie(
            "session",
            LOGISTICS_SESSION,
            httponly=True,
            samesite="Lax",
        )
        return response
    return jsonify(error_code="AUTH_FAILED", msg="登录失败"), 401


def require_logistics_cookie():
    """Return an authentication error when a logistics Cookie is missing."""
    if request.cookies.get("session") != LOGISTICS_SESSION:
        return jsonify(code=40100, data=False, message="Cookie 无效或已过期"), 401
    return None


@app.post("/dar/user/addUser")
def add_user():
    data = request_data()
    required = (data.get("username"), data.get("role_id"), data.get("token"))
    if all(required):
        return jsonify(error_code="0000", msg="新增成功")
    return jsonify(error_code="4000", msg="新增失败")


@app.post("/dar/user/updateUser")
def update_user():
    data = request_data()
    required = (data.get("username"), data.get("password"), data.get("role_id"))
    if all(required):
        return jsonify(error_code="0000", msg="更新成功")
    return jsonify(error_code="4000", msg="更新失败")


@app.post("/dar/user/deleteUser")
def delete_user():
    data = request_data()
    if str(data.get("user_id", "")) == "123839387391912":
        return jsonify(error_code="0000", msg="删除成功")
    return jsonify(error_code="4000", msg="删除失败")


@app.post("/dar/user/queryUser")
def query_user():
    data = request_data()
    if str(data.get("user_id", "")) == "123839387391912":
        return jsonify(
            error_code="0000",
            msg="查询成功",
            msg_code=200,
            user={"user_id": "123839387391912", "username": "testadduser"},
        )
    return jsonify(error_code="4000", msg="查询失败", msg_code=404)


@app.get("/coupApply/cms/goodsList")
def goods_list():
    return jsonify(
        error_code="0000",
        goodsList=[
            {"goodsId": "1001", "name": "示例商品一", "price": "128"},
            {"goodsId": "1002", "name": "示例商品二", "price": "256"},
        ],
    )


@app.post("/coupApply/cms/productDetail")
def product_detail():
    data = request_data()
    product_id = str(data.get("pro_id", ""))
    # The single-interface case deliberately passes the whole ID list and
    # expects the validation response; scenario tests pass one concrete ID.
    if not product_id or "," in product_id:
        return jsonify(error_code="4000", message="商品编号格式错误")
    return jsonify(
        error_code="0000",
        product={"goodsId": product_id, "name": "示例商品", "price": "128"},
    )


@app.post("/coupApply/cms/placeAnOrder")
def place_order():
    data = request_data()
    if not data.get("goods_id"):
        return jsonify(error_code="4000", message="提交订单失败"), 400
    with _state_lock:
        order_number = str(next(_order_ids))
        _orders[order_number] = {"status": "1", "logistics_status": "0"}
    return jsonify(
        error_code="0000",
        message="提交订单成功",
        orderNumber=order_number,
        userId="127839112",
    )


@app.post("/coupApply/cms/orderPay")
def order_pay():
    data = request_data()
    if not data.get("orderNumber") or not data.get("userId"):
        return jsonify(error_code="4000", message="订单支付失败"), 400
    order_number = str(data.get("orderNumber"))
    if order_number in _orders:
        _orders[order_number]["status"] = "0"
    return jsonify(error_code="0000", message="订单支付成功")


@app.post("/coupApply/cms/shoppingJoinCart")
def shopping_join_cart():
    data = request_data()
    goods_id = str(data.get("goods_id", ""))
    if not goods_id or not data.get("count") or not data.get("price"):
        return jsonify(error_code="4000", message="添加购物车失败"), 400
    _cart[goods_id] = {
        "goods_id": goods_id,
        "count": int(data.get("count")),
        "price": str(data.get("price")),
    }
    return jsonify(
        cartList=list(_cart.values()),
        createTime="2026-09-29 10:00:00",
        error="",
        error_code="0000",
        message="success",
        translate_language="zh-CN",
        userId="127839112",
    )


@app.post("/coupApply/cms/delCart")
def delete_cart_item():
    data = request_data()
    product_id = str(data.get("productId", ""))
    if not product_id:
        return jsonify(error_code="4000", message="购物车商品删除失败"), 400
    _cart.pop(product_id, None)
    return jsonify(
        createTime="2026-09-29 10:00:00",
        error="",
        error_code="0000",
        message="success",
        translate_language="zh-CN",
        userId="127839112",
    )


@app.post("/coupApply/cms/checkOrderStatus")
def check_order_status():
    data = request_data()
    if not data.get("orderNumber"):
        return jsonify(error_code="4000", status="1"), 400
    order_number = str(data.get("orderNumber"))
    status = _orders.get(order_number, {}).get("status", "0")
    return jsonify(error_code="0000", status=status)


@app.post("/coupApply/cms/checkLogisticsStatus")
def check_logistics_status():
    data = request_data()
    if not data.get("orderNumber"):
        return jsonify(error_code="4000", status="0"), 400
    order_number = str(data.get("orderNumber"))
    status = _orders.get(order_number, {}).get("logistics_status", "0")
    return jsonify(
        error="",
        error_code="0000",
        queryTime="2026-09-29 10:00:00",
        status=status,
        translate_language="zh-CN",
    )


@app.post("/coupApply/cms/shoppingInventory")
def shopping_inventory():
    data = request_data()
    if not data.get("goodsId") or data.get("count") is None:
        return jsonify(error_code="4000", message="库存参数不完整"), 400
    count_value = int(data.get("count"))
    status = "0" if count_value <= 5 else "1"
    error = "" if status == "0" else "商品库存不足"
    return jsonify(
        createTime="2026-09-29 10:00:00",
        error=error,
        error_code="0000",
        status=status,
        translate_language="zh-CN",
    )


# ---------------------------------------------------------------------------
# Logistics project endpoints.  They form a deterministic local test double
# for the 17 interfaces documented in the supplied project specification.
# ---------------------------------------------------------------------------


@app.route("/api/order/customer/orderPlan/getMaterial", methods=["GET", "POST"])
def logistics_get_material():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    return jsonify(
        code=20000,
        data=True,
        material=[
            "1676511586856882178",
            "1676511586856882134",
            "1676511524756882178",
        ],
        message="操作成功",
    )


@app.post("/api/order/customer/orderPlan/create")
def logistics_create_order():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    data = request_data()
    if not data.get("orderInfo") or not data.get("orderCapacityList"):
        return jsonify(code=40000, data=False, message="订单参数不完整"), 400
    with _state_lock:
        order_no = "DD%s" % next(_logistics_order_ids)
        item_id = "ITEM%s" % order_no[2:]
        _logistics_orders[order_no] = {
            "status": "created",
            "itemId": item_id,
            "payload": data,
        }
    return jsonify(
        code=20000,
        data=True,
        itemId=item_id,
        message="操作成功",
        orderNo=order_no,
    )


@app.post("/api/order/pc/order/master/receive")
def logistics_master_receive():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    data = request_data()
    order_id = str(data.get("orderId", ""))
    if order_id not in _logistics_orders:
        return jsonify(code=40000, data=False, message="订单不存在"), 404
    _logistics_orders[order_id]["status"] = "master_received"
    return jsonify(code=20000, data=True, message="操作成功")


@app.post("/api/order/pc/order/assign")
def logistics_assign_order():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    data = request_data()
    order_id = str(data.get("orderId", ""))
    if order_id not in _logistics_orders or not data.get("orgId"):
        return jsonify(code=40000, data=False, message="订单或物流公司不存在"), 400
    _logistics_orders[order_id]["status"] = "assigned"
    _logistics_orders[order_id]["orgId"] = str(data.get("orgId"))
    return jsonify(code=20000, data=True, message="操作成功")


@app.post("/api/order/pc/order/trans/receive")
def logistics_trans_receive():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    data = request_data()
    order_id = str(data.get("orderId", ""))
    if order_id not in _logistics_orders:
        return jsonify(code=40000, data=False, message="订单不存在"), 404
    logistics_order_id = "WL%s" % order_id[2:]
    _logistics_orders[order_id]["status"] = "trans_received"
    _logistics_orders[order_id]["logisticsOrderId"] = logistics_order_id
    return jsonify(
        code=20000,
        data=True,
        itemId=_logistics_orders[order_id]["itemId"],
        logisticsOrderId=logistics_order_id,
        message="操作成功",
    )


@app.post("/api/order/pc/logisticsOrder/handSplitOrder")
def logistics_split_order():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    data = request_data()
    if not data.get("logisticsOrderId") or not data.get("list"):
        return jsonify(code=40000, data=False, message="拆单参数不完整"), 400
    return jsonify(
        code=20000,
        data=True,
        logisticsStatus="1",
        message="操作成功",
    )


@app.post("/api/order/pc/logisticsOrder/handCapacityDispatch")
def logistics_dispatch():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    data = request_data()
    if not isinstance(data, list) or not data or not data[0].get("logisticsOrderId"):
        return jsonify(code=40000, data=False, message="调度参数不完整"), 400
    with _state_lock:
        schedule_no = "DDU%s" % next(_schedule_ids)
        charge_id = "CHARGE%s" % schedule_no[3:]
        _schedules[schedule_no] = {
            "status": "1",
            "payload": data[0],
            "chargeId": charge_id,
        }
    return jsonify(
        code=20000,
        data=True,
        logisticsStatus="1",
        message="操作成功",
        scheduleNo=schedule_no,
    )


@app.post("/api/order/pc/schedule/findPage")
def logistics_schedule_page():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    data = request_data()
    schedule_no = str(data.get("dataValue", ""))
    schedule = _schedules.get(schedule_no)
    if schedule is None:
        return jsonify(code=40000, data=False, message="调度单不存在"), 404
    record = {
        "carrierName": schedule["payload"].get("carrierName"),
        "chargeId": schedule["chargeId"],
        "createTime": "2026-09-29 10:00:00",
        "driverName": schedule["payload"].get("driverName"),
        "id": "SCHEDULE%s" % schedule_no[3:],
        "scheduleNo": schedule_no,
    }
    return jsonify(
        code=20000,
        data={
            "current": int(data.get("current", 1)),
            "pages": "1",
            "records": [record],
            "size": int(data.get("size", 20)),
            "total": "1",
        },
        message="操作成功",
    )


@app.post("/api/order/pc/scheduleDetail/info")
def logistics_schedule_detail():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    data = request_data()
    schedule_no = str(data.get("scheduleNo", ""))
    schedule = _schedules.get(schedule_no)
    if schedule is None:
        return jsonify(code=40000, data=False, message="调度单不存在"), 404
    return jsonify(
        code=20000,
        data={
            "carrierName": schedule["payload"].get("carrierName"),
            "driverName": schedule["payload"].get("driverName"),
            "scheduleNo": schedule_no,
            "scheduleStatus": 3,
            "scheduleStatusDesc": "待确认",
            "vehicleNo": schedule["payload"].get("vehicleNo"),
        },
        message="操作成功",
    )


@app.post("/api/order/app/schedule/confirm")
def logistics_driver_confirm():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    data = request_data()
    schedule_no = str(data.get("scheduleNo", ""))
    if schedule_no not in _schedules:
        return jsonify(code=40000, data=False, message="调度单不存在"), 404
    _schedules[schedule_no]["status"] = "1"
    return jsonify(
        code=20000,
        data=True,
        message="司机确认成功",
        scheduleNoStatus="1",
    )


@app.post("/rpc/srm/inventory")
def logistics_srm_inventory():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    data = request_data()
    schedule_no = str(data.get("scheduleNo", ""))
    if schedule_no not in _schedules or not data.get("weightNo"):
        return jsonify(code=40000, data=False, message="出库参数不完整"), 400
    weight_no = str(data.get("weightNo"))
    _schedules[schedule_no]["weightNo"] = weight_no
    return jsonify(
        code=20000,
        data={"records": [], "scheduleNoStatus": "3", "weightNo": weight_no},
        message="操作成功",
    )


@app.post("/order/feign/dbjlxt")
def logistics_measurement_push():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    data = request_data()
    if not data.get("weightNo"):
        return jsonify(code=40000, data=False, message="司称单号不能为空"), 400
    return jsonify(
        code=20000,
        data={
            "salesReturnNum": float(data.get("spareNum1", 0)) - float(data.get("productNet", 0)),
            "scheduleNoStatus": "7",
            "storageNum": float(data.get("productNet", 0)),
        },
        message="处理成功",
    )


@app.post("/api/order/pc/cost/receiveCost/create/bill")
def logistics_create_bill():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    data = request_data()
    if not data.get("billName") or not data.get("ids"):
        return jsonify(code=40000, data=False, message="对账单参数不完整"), 400
    with _state_lock:
        reconciliation_no = "DZ%s" % next(_reconciliation_ids)
    return jsonify(
        code=20000,
        data=True,
        message="操作成功",
        reconciliationNum=reconciliation_no,
    )


@app.post("/api/order/pc/cost/payCost/page")
def logistics_bill_detail():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    data = request_data()
    cost_bill_id = str(data.get("costBillId", ""))
    if not cost_bill_id:
        return jsonify(code=40000, data=False, message="对账单号不能为空"), 400
    return jsonify(
        code=20000,
        data={
            "current": str(data.get("current", 1)),
            "pages": "1",
            "records": [
                {
                    "carrierName": "长凡贸易有限公司",
                    "costBillId": cost_bill_id,
                    "freightPrice": 53,
                    "totalMoney": "7950",
                }
            ],
            "size": str(data.get("size", 200)),
            "total": "1",
        },
        message="操作成功",
    )


@app.post("/api/user/pc/carrier/carrier/add")
def logistics_add_carrier():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    data = request_data()
    if len(str(data.get("password", ""))) != 32:
        return jsonify(code=40000, message="承运商密码设置错误"), 400
    if not data.get("carrierName") or not data.get("contactTel"):
        return jsonify(code=40000, message="承运商参数不完整"), 400
    with _state_lock:
        carrier_id = str(next(_carrier_ids))
        _carriers[carrier_id] = dict(data)
    return jsonify(
        carrierId=carrier_id,
        code=20000,
        createTime="2026-09-29 10:00:00",
        data=[],
        message="操作成功",
    )


@app.post("/api/user/pc/carrier/cys/findPage")
def logistics_carrier_page():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    records = [
        {"carrierId": carrier_id, "carrierName": value.get("carrierName")}
        for carrier_id, value in _carriers.items()
    ]
    return jsonify(
        code=20000,
        data={"current": 1, "pages": "1", "records": records, "total": str(len(records))},
        message="操作成功",
    )


@app.post("/api/user/pc/carrier/carrier/delete")
def logistics_delete_carrier():
    auth_error = require_logistics_cookie()
    if auth_error:
        return auth_error
    data = request_data()
    carrier_id = str(data.get("carrierId", ""))
    if carrier_id not in _carriers:
        return jsonify(code=40000, data=False, message="承运商不存在"), 404
    _carriers.pop(carrier_id)
    return jsonify(
        code=20000,
        createTime="2026-09-29 10:00:00",
        data=[],
        message="操作成功",
    )


@app.errorhandler(404)
def not_found(_error):
    return jsonify(error_code="404", message="接口不存在"), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8787, debug=False, use_reloader=False)

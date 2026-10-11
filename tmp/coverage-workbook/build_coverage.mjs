import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "/Users/huangdeyang/pythonproject/outputs/01a0cc35-f9c7-7751-a49a-2145c156585f";
const previewPath = "/Users/huangdeyang/pythonproject/tmp/coverage-workbook/coverage-preview.png";
const outputPath = `${outputDir}/接口覆盖率清单.xlsx`;
const fontName = "Arial";

const rows = [
  [1, "电子商务", "商品浏览", "获取商品列表", "GET", "/coupApply/cms/goodsList", "5-6", "testcase/ProductManager/getProductList.yaml", 1, "已实现", "通过", "待验证", "会话登录后使用 token", "提取商品ID列表"],
  [2, "电子商务", "商品浏览", "获取商品详情", "POST", "/coupApply/cms/productDetail", "6-7", "testcase/ProductManager/productDetail.yaml", 1, "已实现", "通过", "待验证", "依赖商品ID", "已修正为正向详情校验"],
  [3, "电子商务", "订单", "提交订单", "POST", "/coupApply/cms/placeAnOrder", "7-8", "testcase/ProductManager/commitOrder.yaml", 1, "已实现", "通过", "待验证", "依赖商品ID", "提取订单号和用户ID"],
  [4, "电子商务", "订单", "订单支付", "POST", "/coupApply/cms/orderPay", "8-9", "testcase/ProductManager/orderPay.yaml", 1, "已实现", "通过", "待验证", "依赖订单号和用户ID", "支付成功后订单状态为已支付"],
  [5, "电子商务", "购物车", "添加购物车", "POST", "/coupApply/cms/shoppingJoinCart", "9-10", "testcase/ProductManager/shoppingJoinCart.yaml", 1, "已实现", "通过", "待验证", "依赖商品ID", "新增覆盖"],
  [6, "电子商务", "购物车", "删除购物车商品", "POST", "/coupApply/cms/delCart", "10-11", "testcase/ProductManager/delCart.yaml", 1, "已实现", "通过", "待验证", "依赖商品ID", "新增覆盖"],
  [7, "电子商务", "订单", "校验商品订单状态", "POST", "/coupApply/cms/checkOrderStatus", "11-12", "testcase/ProductManager/checkOrderStatus.yaml", 1, "已实现", "通过", "待验证", "依赖订单号", "新增单接口覆盖，业务场景也已覆盖"],
  [8, "电子商务", "物流状态", "校验商品物流状态", "POST", "/coupApply/cms/checkLogisticsStatus", "12-13", "testcase/ProductManager/checkLogisticsStatus.yaml", 1, "已实现", "通过", "待验证", "依赖订单号", "新增覆盖"],
  [9, "电子商务", "库存", "校验商品库存", "POST", "/coupApply/cms/shoppingInventory", "13-14", "testcase/ProductManager/shoppingInventory.yaml", 2, "已实现", "通过", "待验证", "依赖商品ID", "覆盖库存正常和库存不足"],
  [10, "物流", "下单", "获取下单物料信息", "GET", "/api/order/customer/orderPlan/getMaterial", "14-15", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie", "提取物料ID"],
  [11, "物流", "下单", "货主下订单", "POST", "/api/order/customer/orderPlan/create", "15-17", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie、物料ID", "提取订单号和物料明细ID"],
  [12, "物流", "集团调度", "集团接收货主订单", "POST", "/api/order/pc/order/master/receive", "17-18", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie、订单号", "核心链路"],
  [13, "物流", "集团调度", "集团分配订单给物流公司", "POST", "/api/order/pc/order/assign", "18-19", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie、订单号、组织ID", "核心链路"],
  [14, "物流", "物流接单", "物流公司接单", "POST", "/api/order/pc/order/trans/receive", "19-20", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie、订单号", "提取物流订单号"],
  [15, "物流", "物流接单", "物流公司拆分订单", "POST", "/api/order/pc/logisticsOrder/handSplitOrder", "20-21", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie、物流订单号、物料明细ID", "核心链路"],
  [16, "物流", "运输调度", "物流公司调度派车", "POST", "/api/order/pc/logisticsOrder/handCapacityDispatch", "21-22", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie、物流订单号", "提取调度单号"],
  [17, "物流", "运输调度", "获取调度单页面列表", "POST", "/api/order/pc/schedule/findPage", "22-24", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie、调度单号", "提取记录ID和费用ID"],
  [18, "物流", "运输调度", "获取调度单详情", "POST", "/api/order/pc/scheduleDetail/info", "24-27", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie、调度单号", "核心链路"],
  [19, "物流", "司机运输", "司机APP端确认运输", "POST", "/api/order/app/schedule/confirm", "27-28", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie、调度单号", "核心链路"],
  [20, "物流", "出入库", "SRM系统推送运量出库信息", "POST", "/rpc/srm/inventory", "28-30", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie、调度单号", "提取司称单号"],
  [21, "物流", "出入库", "计量系统推送入库退货量", "POST", "/order/feign/dbjlxt", "30-31", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie、司称单号", "校验入库量和退货量处理"],
  [22, "物流", "费用结算", "创建应付对账单", "POST", "/api/order/pc/cost/receiveCost/create/bill", "31-32", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie、调度单号、费用ID", "提取对账单号"],
  [23, "物流", "费用结算", "获取应付对账单详情及运费", "POST", "/api/order/pc/cost/payCost/page", "32-34", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie、对账单号", "核心链路"],
  [24, "物流", "承运商", "添加承运商", "POST", "/api/user/pc/carrier/carrier/add", "34-36", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie、MD5密码", "提取承运商ID"],
  [25, "物流", "承运商", "获取承运商列表", "POST", "/api/user/pc/carrier/cys/findPage", "36-37", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie", "查询本次创建的承运商"],
  [26, "物流", "承运商", "删除承运商", "POST", "/api/user/pc/carrier/carrier/delete", "37-38", "testcase/Logistics/logistics_scenario.yml", 1, "已实现", "通过", "待验证", "Cookie、承运商ID", "清理测试数据"],
];

const workbook = Workbook.create();
const sheet = workbook.worksheets.add("覆盖率清单");
sheet.showGridLines = false;
sheet.tabColor = "#1F4E78";

sheet.getRange("A2").values = [["电商与物流接口覆盖率清单"]];
sheet.getRange("A2").format.font = { name: fontName, size: 16, bold: true, color: "#1F2937" };
sheet.getRange("A3:N3").format.borders = { bottom: { style: "thin", color: "#9CA3AF" } };

sheet.getRange("A4:N4").values = [[
  "接口总数", null,
  "已自动化", null,
  "实现覆盖率", null,
  "本地通过", null,
  "本地通过率", null,
  "真实环境已验证", null,
  "真实环境验证率", null,
]];
sheet.getRange("B4").formulas = [["=COUNTA(A11:A36)"]];
sheet.getRange("D4").formulas = [["=COUNTIFS(J11:J36,\"已实现\")"]];
sheet.getRange("F4").formulas = [["=D4/B4"]];
sheet.getRange("H4").formulas = [["=COUNTIFS(K11:K36,\"通过\")"]];
sheet.getRange("J4").formulas = [["=H4/B4"]];
sheet.getRange("L4").formulas = [["=COUNTIFS(L11:L36,\"已验证\")"]];
sheet.getRange("N4").formulas = [["=L4/B4"]];

for (const address of ["A4", "C4", "E4", "G4", "I4", "K4", "M4"]) {
  sheet.getRange(address).format = {
    fill: "#DCE6F1",
    font: { name: fontName, bold: true, color: "#1F2937" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
  };
}
for (const address of ["B4", "D4", "F4", "H4", "J4", "L4", "N4"]) {
  sheet.getRange(address).format = {
    fill: "#F3F6FA",
    font: { name: fontName, bold: true, color: "#1F2937" },
    horizontalAlignment: "center",
    verticalAlignment: "center",
  };
}
sheet.getRange("F4").format.numberFormat = "0.0%";
sheet.getRange("J4").format.numberFormat = "0.0%";
sheet.getRange("N4").format.numberFormat = "0.0%";
sheet.getRange("A4:N4").format.borders = { preset: "outside", style: "thin", color: "#9CA3AF" };

sheet.getRange("A6").values = [["口径：实现覆盖率表示文档端点已有自动化用例；本地通过率表示用例通过本项目 Flask 测试替身；真实环境验证率仅统计实际物流或电商环境执行结果。"]];
sheet.getRange("A6").format.font = { name: fontName, size: 10, italic: true, color: "#4B5563" };
sheet.getRange("A7").values = [["来源：电子商务项目&物流项目接口文档.pdf，共38页，文档日期 2023-08-22。"]];
sheet.getRange("A7").format.font = { name: fontName, size: 10, italic: true, color: "#4B5563" };

const headers = [[
  "序号", "项目", "业务阶段", "接口名称", "方法", "接口路径", "文档页码",
  "自动化用例文件", "用例数", "自动化状态", "本地结果", "真实环境",
  "鉴权与依赖", "备注",
]];
sheet.getRange("A10:N10").values = headers;
sheet.getRange("A11:N36").values = rows;

sheet.getRange("A10:N10").format = {
  fill: "#1F4E78",
  font: { name: fontName, bold: true, color: "#FFFFFF", size: 10 },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  wrapText: true,
  borders: {
    insideVertical: { style: "thin", color: "#FFFFFF" },
    bottom: { style: "thin", color: "#FFFFFF" },
  },
};

sheet.getRange("A11:N36").format = {
  font: { name: fontName, size: 10, color: "#1F2937" },
  verticalAlignment: "center",
  borders: { insideHorizontal: { style: "thin", color: "#D1D5DB" } },
};
sheet.getRange("A11:A36").format.horizontalAlignment = "center";
sheet.getRange("B11:C36").format.horizontalAlignment = "center";
sheet.getRange("E11:E36").format.horizontalAlignment = "center";
sheet.getRange("G11:G36").format.horizontalAlignment = "center";
sheet.getRange("I11:L36").format.horizontalAlignment = "center";
sheet.getRange("H11:H36").format.wrapText = true;
sheet.getRange("M11:N36").format.wrapText = true;

sheet.getRange("J11:J36").conditionalFormats.add("containsText", {
  text: "已实现",
  format: { fill: "#DCFCE7", font: { color: "#166534", bold: true } },
});
sheet.getRange("K11:K36").conditionalFormats.add("containsText", {
  text: "通过",
  format: { fill: "#DCFCE7", font: { color: "#166534", bold: true } },
});
sheet.getRange("L11:L36").conditionalFormats.add("containsText", {
  text: "待验证",
  format: { fill: "#FEF3C7", font: { color: "#92400E", bold: true } },
});

const table = sheet.tables.add("A10:N36", true, "InterfaceCoverageTable");
table.style = "TableStyleMedium2";
table.showFilterButton = true;

sheet.getRange("A:A").format.columnWidth = 7;
sheet.getRange("B:B").format.columnWidth = 12;
sheet.getRange("C:C").format.columnWidth = 13;
sheet.getRange("D:D").format.columnWidth = 25;
sheet.getRange("E:E").format.columnWidth = 9;
sheet.getRange("F:F").format.columnWidth = 48;
sheet.getRange("G:G").format.columnWidth = 11;
sheet.getRange("H:H").format.columnWidth = 46;
sheet.getRange("I:I").format.columnWidth = 9;
sheet.getRange("J:L").format.columnWidth = 13;
sheet.getRange("M:M").format.columnWidth = 30;
sheet.getRange("N:N").format.columnWidth = 34;
sheet.getRange("4:4").format.rowHeight = 30;
sheet.getRange("10:10").format.rowHeight = 34;
sheet.getRange("11:36").format.rowHeight = 34;
sheet.freezePanes.freezeRows(10);
sheet.freezePanes.freezeColumns(2);

workbook.recalculate();

const check = await workbook.inspect({
  kind: "table",
  range: "覆盖率清单!A2:N15",
  include: "values,formulas",
  tableMaxRows: 15,
  tableMaxCols: 14,
});
console.log(check.ndjson);

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!",
  options: { useRegex: true, maxResults: 100 },
  summary: "final formula error scan",
});
console.log(errors.ndjson);

await fs.mkdir(outputDir, { recursive: true });
const preview = await workbook.render({
  sheetName: "覆盖率清单",
  range: "A1:N36",
  scale: 1,
  format: "png",
});
await fs.writeFile(previewPath, new Uint8Array(await preview.arrayBuffer()));

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

const savedInput = await FileBlob.load(outputPath);
const savedWorkbook = await SpreadsheetFile.importXlsx(savedInput);
const savedCheck = await savedWorkbook.inspect({
  kind: "table",
  range: "覆盖率清单!A4:N11",
  include: "values,formulas",
  tableMaxRows: 8,
  tableMaxCols: 14,
});
console.log(savedCheck.ndjson);
console.log(JSON.stringify({ outputPath, previewPath }));

"""Generate four vector UML/architecture pages and the editable diagrams.net source.

Requires Python 3.11+ and reportlab. Coordinates use a top-left origin in points.
The same scene data feeds PDF and draw.io, so labels and relationships agree.
"""

import math
import xml.etree.ElementTree as ET
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parents[1]
W, H = 842, 595
INK, TEAL, MUTED = "#15323F", "#147D79", "#526570"
LIGHT, BORDER, AMBER = "#EFF7F5", "#B5C9CE", "#F5EEDC"
PAGES = []
items = []


def shape(kind, x, y, w, h, label="", fill="#FFFFFF", stroke=BORDER, size=10, bold=False, align="center"):
    item = dict(kind=kind, x=x, y=y, w=w, h=h, label=label, fill=fill, stroke=stroke,
                size=size, bold=bold, align=align)
    items.append(item)
    return item


def text(x, y, w, h, label, size=10, bold=False, color=INK, align="left"):
    item = shape("text", x, y, w, h, label, fill=None, stroke=None, size=size, bold=bold, align=align)
    item["color"] = color


def line(points, label="", lx=None, ly=None, lw=200, arrow=False, dashed=False, color=MUTED):
    items.append(dict(kind="line", points=points, arrow=arrow, dashed=dashed, color=color))
    if label:
        text(lx, ly, lw, 25, label, size=9, color=color, align="center")


def actor(x, y, label):
    shape("ellipse", x - 9, y, 18, 18, fill="#FFFFFF", stroke=INK)
    line([(x, y + 18), (x, y + 48)], color=INK)
    line([(x - 18, y + 30), (x + 18, y + 30)], color=INK)
    line([(x, y + 48), (x - 17, y + 68)], color=INK)
    line([(x, y + 48), (x + 17, y + 68)], color=INK)
    text(x - 66, y + 73, 132, 40, label, size=10, bold=True, align="center")


def page(number, title, subtitle):
    global items
    items = []
    PAGES.append((title, items))
    shape("rect", 0, 0, W, 8, fill=TEAL, stroke=None)
    text(36, 23, 650, 18, "ЛАБОРАТОРИ 5  /  НИЙТИЙН ДУГУЙ ТҮРЭЭСИЙН СИСТЕМ", size=9, bold=True, color=TEAL)
    text(36, 47, 760, 32, title, size=24, bold=True)
    text(36, 85, 765, 25, subtitle, size=10, color=MUTED)
    line([(36, 551), (806, 551)], color=BORDER)
    text(36, 561, 650, 16, "Баг-17 · Ө. Анар B242270129 · О. Хүслэн B242270073 · Н. Мөнхбаяр B242270058", size=8, color=MUTED)
    text(750, 559, 56, 18, f"{number} / 4", size=10, bold=True, align="right")


def build_scenes():
    page(1, "01  Use Case Diagram", "Lab 2-ын үндсэн хэрэглэгчийн зорилгууд ба системийн хил")
    shape("rect", 186, 121, 464, 363, fill="#FAFCFC", stroke=BORDER)
    text(205, 128, 423, 22, "Нийтийн дугуй түрээсийн систем", size=11, bold=True, align="center")
    actor(77, 262, "Хэрэглэгч\n(жуулчин багтана)")
    actor(749, 210, "Системийн\nоператор")
    actor(749, 372, "Засварын\nажилтан")
    labels = [
        "Бүртгүүлэх · US-01", "Нэвтрэх · US-02", "Зогсоол, сул дугуй харах\nUS-03, US-04",
        "QR кодоор түрээс эхлүүлэх\nUS-05", "Хугацаа, төлбөр харах · US-06",
        "Дугуй буцаах · US-07", "Төлбөр төлөх · US-08",
    ]
    centers = [172, 218, 264, 310, 356, 402, 448]
    for center in centers:
        line([(95, 292), (209, center)], color="#91A8AD")
    for center, label in zip(centers, labels):
        shape("ellipse", 209, center - 18, 254, 36, label, fill="#FFFFFF", stroke=TEAL, size=10)
    line([(579, 248), (731, 240)], color="#91A8AD")
    shape("ellipse", 482, 215, 146, 66, "Зогсоолын нөөц\nхянах · US-14", fill=LIGHT, stroke=TEAL, size=10)
    line([(579, 408), (731, 402)], color="#91A8AD")
    shape("ellipse", 482, 375, 146, 66, "Засварын төлөв\nшинэчлэх · US-15", fill=LIGHT, stroke=TEAL, size=10)
    text(36, 497, 770, 42,
         "QR түрээсийн урьдчилсан нөхцөл: хэрэглэгч нэвтэрсэн байна. Нэвтрэлтийг «include» гэж хүчээр холбогоогүй.\n"
         "Энэ нь үндсэн урсгалын зураг; US-09–US-13 нь Lab 2-ын backlog-д хэвээр. Админд тусдаа story хараахан байхгүй.",
         size=9, color=MUTED)

    page(2, "02  Class Diagram", "5 үндсэн класс · attribute, operation, multiplicity · логик загвар")
    def cls(x, y, w, title, attributes, methods):
        ah = len(attributes) * 16 + 12
        mh = len(methods) * 16 + 12
        shape("rect", x, y, w, 30 + ah + mh, fill="#FFFFFF", stroke=TEAL)
        shape("rect", x, y, w, 30, title, fill=LIGHT, stroke=TEAL, size=12, bold=True)
        text(x + 10, y + 37, w - 20, ah - 4, "\n".join(attributes), size=9)
        line([(x, y + 30 + ah), (x + w, y + 30 + ah)], color=BORDER)
        text(x + 10, y + 37 + ah, w - 20, mh - 4, "\n".join(methods), size=9)
    # Relationships are behind the class boxes, with endpoint multiplicities.
    line([(255, 203), (283, 203), (283, 278), (315, 278)])
    text(260, 183, 22, 18, "1", size=10)
    text(288, 255, 25, 18, "0..*", size=10)
    text(263, 218, 49, 30, "үүсгэнэ", size=8, align="center")
    line([(525, 278), (556, 278), (556, 203), (585, 203)])
    text(529, 254, 28, 18, "0..*", size=10)
    text(560, 183, 22, 18, "1", size=10)
    text(530, 218, 53, 30, "ашиглана", size=8, align="center")
    line([(690, 298), (690, 366)])
    text(698, 300, 30, 16, "0..*", size=10)
    text(698, 345, 40, 16, "0..1", size=10)
    text(726, 323, 65, 24, "байрлана", size=8)
    line([(315, 398), (283, 398), (283, 421), (255, 421)])
    text(287, 379, 22, 16, "1", size=10)
    text(258, 425, 39, 16, "0..1", size=10)
    text(259, 397, 50, 18, "төлбөр", size=8)
    cls(45, 132, 210, "User", ["- userId: int", "- fullName: String", "- email: String", "- passwordHash: String", "- role: UserRole"], ["+ verifyPassword(): bool", "+ updateProfile(): void"])
    cls(315, 238, 210, "Rental", ["- rentalId: int", "- startTime: DateTime", "- endTime: DateTime?", "- status: RentalStatus", "- cost: Decimal"], ["+ start(): void", "+ end(): void", "+ calculateCost(): Decimal"])
    cls(585, 132, 210, "Bike", ["- bikeId: int", "- qrCode: String", "- status: BikeStatus", "- currentStationId: int?"], ["+ markRented(): void", "+ markAvailable(): void", "+ reportDamage(): void"])
    cls(585, 366, 210, "Station", ["- stationId: int", "- name: String", "- location: GeoPoint", "- capacity: int"], ["+ availableBikes(): int", "+ hasFreeDock(): bool"])
    cls(45, 366, 210, "Payment", ["- paymentId: int", "- amount: Decimal", "- status: PaymentStatus", "- providerRef: String?"], ["+ request(): void", "+ confirm(): void"])
    text(36, 520, 770, 26, "Тайлбар: дугуй түрээстэй үед зогсоолгүй (0..1). Түрээсийн төлбөр үүсээгүй байж болно (0..1).\nUserRole: CUSTOMER / OPERATOR / MAINTENANCE. Role нь заавал удамшил байх шаардлагагүй.", size=8, color=MUTED)

    page(3, "03  Sequence Diagram", "US-05 · QR кодоор дугуй түрээслэх · амжилт ба боломжгүй нөхцөл")
    xs = [82, 305, 527, 750]
    titles = ["Хэрэглэгч", "Мобайл UI", "Rental Service", "Өгөгдлийн сан"]
    for x, title in zip(xs, titles):
        shape("rect", x - 69, 128, 138, 35, title, fill=LIGHT, stroke=TEAL, size=10, bold=True)
        line([(x, 163), (x, 480)], dashed=True, color=BORDER)
    shape("rect", 518, 202, 18, 239, fill="#D6EBE8", stroke=TEAL)
    def message(a, b, y, label, dashed=False):
        line([(xs[a], y), (xs[b], y)], arrow=True, dashed=dashed, color=INK)
        text(min(xs[a], xs[b]) + 5, y - 25, abs(xs[b] - xs[a]) - 10, 23, label, size=9, align="center")
    message(0, 1, 193, "1. QR код уншуулах")
    message(1, 2, 228, "2. startRental(session, qr)")
    message(2, 3, 264, "3. reserveAndCreate(userId, qr)")
    message(3, 2, 300, "4. rentalId эсвэл боломжгүй", dashed=True)
    shape("rect", 36, 321, 770, 155, fill=None, stroke=BORDER)
    text(43, 323, 60, 20, "alt", size=10, bold=True)
    text(315, 326, 365, 20, "[дугуй сул биш / идэвхтэй түрээс байгаа]", size=9, bold=True)
    message(2, 1, 369, "5a. Алдаа: түрээс эхлэх боломжгүй", dashed=True)
    line([(36, 388), (806, 388)], dashed=True, color=BORDER)
    text(315, 393, 365, 20, "[түрээс амжилттай бүртгэгдсэн]", size=9, bold=True)
    message(2, 1, 435, "5b. Түрээсийн ID, эхлэх цаг", dashed=True)
    message(1, 0, 470, "6. Түрээс эхэлснийг харуулах", dashed=True)
    text(36, 493, 770, 49,
         "Урьдчилсан нөхцөл: хэрэглэгч нэвтэрсэн, хүчинтэй QR кодтой. Нэг transaction дотор дугуйн сул төлөв ба хэрэглэгчийн\n"
         "идэвхтэй түрээсийг шалгаж, дугуйг RENTED болгон түрээс үүсгэнэ; бүтэлгүй бол rollback хийнэ. Ингэснээр давхар түрээс үүсэхгүй.\n"
         "Энэ нь логик түрээсийн урсгал; бодит IoT түгжээний баталгаажуулалт, нөхөн сэргээх урсгалыг дараагийн загварт нарийвчилна.", size=8.5, color=MUTED)

    page(4, "04  Архитектурын эскиз", "Layered Architecture · Presentation → Business → Data")
    layers = [
        (127, "1  PRESENTATION", ["Хэрэглэгчийн мобайл UI", "Операторын вэб UI", "Засварын ажилтны UI"]),
        (237, "2  BUSINESS", ["Auth Service", "Station / Rental Service", "Payment / Notification"]),
        (347, "3  DATA", ["User, Station", "Bike, Rental", "Payment / Repository"]),
    ]
    for y, title, components in layers:
        shape("rect", 36, y, 590, 87, fill="#FAFCFC", stroke=BORDER)
        text(49, y + 9, 550, 20, title, size=10, bold=True, color=TEAL)
        for index, component in enumerate(components):
            shape("rect", 49 + index * 190, y + 35, 177, 37, component, fill=LIGHT, stroke=BORDER, size=9)
    line([(331, 214), (331, 237)], arrow=True, color=TEAL)
    text(350, 215, 180, 20, "HTTP / API", size=8, color=MUTED)
    line([(331, 324), (331, 347)], arrow=True, color=TEAL)
    text(350, 326, 180, 20, "Repository / SQL", size=8, color=MUTED)
    shape("rect", 661, 255, 145, 65, "Гадаад төлбөрийн\nүйлчилгээ", fill=AMBER, stroke="#B19B6D", size=10)
    line([(626, 288), (661, 288)], arrow=True, color=TEAL)
    text(659, 330, 148, 80, "Төлбөрийн adapter нь\nBusiness давхаргад байна.\nUI нь DB-д шууд\nхандахгүй.", size=9, color=MUTED)
    text(36, 449, 770, 20, "Сонгосон үндэслэл", size=12, bold=True)
    text(36, 477, 770, 63,
         "Гурван гишүүнтэй баг UI, бизнес логик, өгөгдлийн ажлыг тусгаарлан хөгжүүлэхэд Layered архитектур тохиромжтой.\n"
         "Мобайл болон операторын вэб ижил service-ийг ашиглах тул түрээс, төлбөрийн дүрэм давхардахгүй.\n"
         "Repository интерфейс ашигласнаар өгөгдлийн сан эсвэл UI өөрчлөгдөхөд бусад давхаргын өөрчлөлт багасна.\n"
         "Төлбөрийн гадаад үйлчилгээг adapter-аар тусгаарлах нь дараагийн өргөтгөл, тест, засвар үйлчилгээг хялбарчилна.", size=9, color=MUTED)


def wrapped_lines(value, max_width, font, size):
    result = []
    for paragraph in value.split("\n"):
        words = paragraph.split()
        if not words:
            result.append("")
            continue
        row = ""
        for word in words:
            candidate = f"{row} {word}".strip()
            if row and pdfmetrics.stringWidth(candidate, font, size) > max_width:
                result.append(row)
                row = word
            else:
                row = candidate
        result.append(row)
    return result


def render_pdf():
    fontdir = Path("/usr/share/fonts/truetype/dejavu")
    pdfmetrics.registerFont(TTFont("DV", str(fontdir / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DV-B", str(fontdir / "DejaVuSans-Bold.ttf")))
    c = canvas.Canvas(str(ROOT / "Lab5_UML_Bag17.pdf"), pagesize=(W, H), invariant=1)
    c.setTitle("Лаборатори 5 - UML ба архитектур - Баг 17")
    c.setAuthor("Баг-17")
    for title, scene in PAGES:
        c.bookmarkPage(title)
        c.addOutlineEntry(title, title)
        for item in scene:
            kind = item["kind"]
            if kind == "line":
                pts = item["points"]
                c.setStrokeColor(HexColor(item["color"]))
                c.setLineWidth(0.9)
                c.setDash(4, 3) if item["dashed"] else c.setDash()
                path = c.beginPath()
                path.moveTo(pts[0][0], H - pts[0][1])
                for x, y in pts[1:]:
                    path.lineTo(x, H - y)
                c.drawPath(path)
                c.setDash()
                if item["arrow"]:
                    x, y = pts[-1]
                    px, py = pts[-2]
                    angle = math.atan2(y - py, x - px)
                    for delta in [-0.45, 0.45]:
                        c.line(x, H - y, x - 7 * math.cos(angle + delta), H - y + 7 * math.sin(angle + delta))
                continue
            x, y, width, height = (item[k] for k in ["x", "y", "w", "h"])
            if item["fill"]:
                c.setFillColor(HexColor(item["fill"]))
            if item["stroke"]:
                c.setStrokeColor(HexColor(item["stroke"]))
            c.setLineWidth(0.8)
            if kind in ["rect", "ellipse"]:
                method = c.rect if kind == "rect" else c.ellipse
                args = (x, H - y - height, width, height) if kind == "rect" else (x, H - y - height, x + width, H - y)
                method(*args, fill=bool(item["fill"]), stroke=bool(item["stroke"]))
            if item["label"]:
                font = "DV-B" if item["bold"] else "DV"
                size = item["size"]
                rows = wrapped_lines(item["label"], width - 8, font, size)
                leading = size * 1.26
                needed = len(rows) * leading
                if needed > height + 1:
                    raise ValueError(f"Text too tall ({needed:.1f}>{height}): {item['label']}")
                top = y + (height - needed) / 2 + size
                c.setFont(font, size)
                c.setFillColor(HexColor(item.get("color", INK)))
                for index, row in enumerate(rows):
                    yy = H - top - index * leading
                    if item["align"] == "center":
                        c.drawCentredString(x + width / 2, yy, row)
                    elif item["align"] == "right":
                        c.drawRightString(x + width - 4, yy, row)
                    else:
                        c.drawString(x + 4, yy, row)
        c.showPage()
    c.save()


def render_drawio():
    root = ET.Element("mxfile", host="app.diagrams.net", type="device")
    for index, (title, scene) in enumerate(PAGES, 1):
        diagram = ET.SubElement(root, "diagram", id=f"lab5-page-{index}", name=title)
        model = ET.SubElement(diagram, "mxGraphModel", dx="842", dy="595", grid="1", gridSize="10",
                              page="1", pageScale="1", pageWidth="842", pageHeight="595")
        cells = ET.SubElement(model, "root")
        ET.SubElement(cells, "mxCell", id="0")
        ET.SubElement(cells, "mxCell", id="1", parent="0")
        for serial, item in enumerate(scene, 2):
            kind = item["kind"]
            if kind == "line":
                style = f"endArrow={'open' if item['arrow'] else 'none'};strokeColor={item['color']};"
                style += "dashed=1;" if item["dashed"] else ""
                cell = ET.SubElement(cells, "mxCell", id=str(serial), style=style, edge="1", parent="1")
                geo = ET.SubElement(cell, "mxGeometry", relative="1", **{"as": "geometry"})
                pts = item["points"]
                for point, name in [(pts[0], "sourcePoint"), (pts[-1], "targetPoint")]:
                    ET.SubElement(geo, "mxPoint", x=str(point[0]), y=str(point[1]), **{"as": name})
                if len(pts) > 2:
                    array = ET.SubElement(geo, "Array", **{"as": "points"})
                    for point in pts[1:-1]:
                        ET.SubElement(array, "mxPoint", x=str(point[0]), y=str(point[1]))
                continue
            styles = ["html=0", "whiteSpace=wrap", "fontFamily=DejaVu Sans", f"fontSize={item['size']}",
                      f"fontStyle={1 if item['bold'] else 0}", f"align={item['align']}", "verticalAlign=middle",
                      f"fillColor={item['fill'] or 'none'}", f"strokeColor={item['stroke'] or 'none'}",
                      f"fontColor={item.get('color', INK)}"]
            if kind == "text":
                styles.append("text")
            elif kind == "ellipse":
                styles.append("ellipse")
            cell = ET.SubElement(cells, "mxCell", id=str(serial), value=item["label"],
                                 style=";".join(styles) + ";", vertex="1", parent="1")
            ET.SubElement(cell, "mxGeometry", x=str(item["x"]), y=str(item["y"]), width=str(item["w"]),
                          height=str(item["h"]), **{"as": "geometry"})
    ET.indent(root)
    ET.ElementTree(root).write(ROOT / "Lab5_UML_Bag17.drawio", encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    build_scenes()
    render_pdf()
    render_drawio()
    print("Generated Lab5_UML_Bag17.pdf and Lab5_UML_Bag17.drawio (4 pages).")

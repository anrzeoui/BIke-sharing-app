# 🚲 Bike Sharing App

## Лабораторийн ажил №2
### Хэрэглэгчийн хэрэгцээг ойлгох ба User Story бичих

**Сэдэв:** Нийтийн дугуй түрээсийн систем (Bike Sharing App)
**Баг-17 Гишүүд:** - Ө. Анар (B242270129)
                   - О. Хүслэн (B242270073)
                   - Н. Мөнхбаяр (B242270058)
---

## 1. Төслийн зорилго

Bike Sharing App нь хотын иргэд, оюутнууд, жуулчид болон бусад хэрэглэгчдэд нийтийн зориулалттай дугуйг хурдан, хялбар түрээслэх боломж олгох систем юм.

Системийн үндсэн зорилго нь хэрэглэгчид:

- Ойролцоох дугуйн зогсоолыг олох
- Сул дугуйн мэдээлэл харах
- QR код ашиглан дугуй түрээслэх
- Түрээсийн хугацаа болон төлбөрийг хянах
- Дугуй буцаах
- Цахимаар төлбөр төлөх
- Түрээсийн түүхээ харах

боломжийг нэг системээр олгоход оршино.

---

## 2. Шийдвэрлэх асуудал

Хот дотор богино зайд зорчих үед автомашин болон нийтийн тээвэр ашиглах нь зарим тохиолдолд цаг хугацаа их шаарддаг.

Мөн:

- Замын түгжрэл
- Авто зогсоолын хүрэлцээ
- Богино зайд зорчих тээврийн хэрэгслийн хэрэгцээ

зэрэг асуудлууд тулгардаг.

Bike Sharing App нь хэрэглэгчдэд богино зайд хурдан зорчих өөр сонголт бий болгож, нийтийн дугуйн ашиглалтыг системтэй удирдах боломж олгоно.

---

## 3. Зорилтот хэрэглэгчид

| Хэрэглэгч | Үүрэг |
|---|---|
| Rider / Хэрэглэгч | Дугуй хайх, түрээслэх, буцаах, төлбөр төлөх |
| Tourist / Жуулчин | Хот дотор богино хугацаагаар дугуй ашиглах |
| System Operator / Оператор | Дугуй болон зогсоолын төлөвийг хянах |
| Maintenance Staff | Эвдэрсэн дугуйг шалгах, засварлах |
| Administrator | Хэрэглэгч болон системийн тохиргоог удирдах |

---

## 4. Үндсэн функцууд

1. Хэрэглэгч бүртгүүлэх
2. Системд нэвтрэх
3. Ойролцоох дугуйн зогсоол хайх
4. Сул дугуйн мэдээлэл харах
5. QR код ашиглан дугуй түрээслэх
6. Түрээсийн хугацаа болон төлбөр хянах
7. Дугуй буцаах
8. Цахим төлбөр төлөх
9. Түрээсийн түүх харах
10. Дугуй урьдчилан захиалах
11. Захиалга цуцлах
12. Эвдэрсэн дугуй мэдээлэх
13. Мэдэгдэл хүлээн авах
14. Зогсоолын дугуйн нөөц хянах
15. Дугуйн засвар үйлчилгээ удирдах

---

# 5. Product Backlog

| ID | User Story | Priority | Notes |
|---|---|---|---|
| US-01 | As a new user, I want to create an account, so that I can use the bike sharing service. | High | Must have |
| US-02 | As a registered user, I want to log in to my account, so that I can access the bike rental features. | High | Must have |
| US-03 | As a rider, I want to see nearby bike stations on a map, so that I can quickly find a bike. | High | Must have |
| US-04 | As a rider, I want to see the number of available bikes at each station, so that I can choose a station that has a bike available. | High | Must have |
| US-05 | As a rider, I want to scan a bike's QR code, so that I can quickly start my rental. | High | Must have |
| US-06 | As a rider, I want to see my current rental time and cost, so that I can monitor my trip and spending. | High | Must have |
| US-07 | As a rider, I want to return a bike at an available station, so that I can finish my rental correctly. | High | Must have |
| US-08 | As a rider, I want to pay my rental fee electronically, so that I can complete my rental without using cash. | High | Must have |
| US-09 | As a rider, I want to view my previous rentals, so that I can review my trips and expenses. | Medium | Should have |
| US-10 | As a rider, I want to reserve an available bike, so that it will still be available when I arrive at the station. | Medium | Should have |
| US-11 | As a rider, I want to cancel my bike reservation, so that another user can use the bike if my plans change. | Medium | Should have |
| US-12 | As a rider, I want to report a damaged bike, so that the operator can repair it and prevent other users from renting it. | Medium | Should have |
| US-13 | As a rider, I want to receive notifications about my rental, so that I know when my rental starts, ends, or requires attention. | Medium | Should have |
| US-14 | As a system operator, I want to monitor bike availability at all stations, so that I can manage bike distribution efficiently. | High | Must have |
| US-15 | As a maintenance worker, I want to view damaged bikes and update their repair status, so that repaired bikes can return to service. | Medium | Should have |

---

# 6. INVEST зарчим

User Story бүрийг INVEST зарчмын дагуу шалгасан.

| Зарчим | Тайлбар |
|---|---|
| Independent | User Story бүр бие даасан |
| Negotiable | Хэрэгжүүлэх арга нь хэлэлцэгдэх боломжтой |
| Valuable | Хэрэглэгчид тодорхой үнэ цэнэ өгнө |
| Estimable | Хөгжүүлэлтийн ажлын хэмжээг үнэлэх боломжтой |
| Small | Нэг Story нь жижиг, тодорхой зорилготой |
| Testable | Үр дүнг тестээр шалгах боломжтой |

### INVEST шалгалт

| ID | I | N | V | E | S | T |
|---|---|---|---|---|---|---|
| US-01 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| US-02 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| US-03 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| US-04 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| US-05 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| US-06 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| US-07 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| US-08 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| US-09 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| US-10 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| US-11 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| US-12 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| US-13 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| US-14 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| US-15 | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

---

# 7. Acceptance Criteria

| ID | Acceptance Criteria |
|---|---|
| US-01 | Хүчинтэй мэдээлэл оруулахад шинэ хэрэглэгчийн бүртгэл үүснэ. |
| US-02 | Зөв мэдээллээр системд нэвтэрч, буруу мэдээлэлд алдаа харуулна. |
| US-03 | Газрын зураг дээр ойролцоох дугуйн зогсоолууд харагдана. |
| US-04 | Зогсоол бүрийн сул дугуйн тоо харагдана. |
| US-05 | Хүчинтэй QR код уншуулахад түрээс эхэлнэ. |
| US-06 | Түрээсийн хугацаа болон одоогийн төлбөр харагдана. |
| US-07 | Дугуйг зөв зогсоолд буцаахад түрээс дуусна. |
| US-08 | Төлбөр амжилттай хийгдэхэд баталгаажуулалт харагдана. |
| US-09 | Өмнөх түрээсүүд огноо, хугацаа, төлбөрийн хамт харагдана. |
| US-10 | Дугуй захиалахад тухайн дугуй захиалагдсан төлөвт орно. |
| US-11 | Захиалга цуцлагдсаны дараа дугуй дахин боломжтой болно. |
| US-12 | Эвдрэлийн мэдээлэл операторт хүрнэ. |
| US-13 | Түрээс эхлэх болон дуусах үед мэдэгдэл ирнэ. |
| US-14 | Оператор бүх зогсоолын дугуйн нөөцийг харах боломжтой байна. |
| US-15 | Засварын ажилтан дугуйн засварын төлөвийг шинэчилж чадна. |

---

# 8. Priority

### High Priority – Must Have

- US-01 – Account Registration
- US-02 – Login
- US-03 – Find Nearby Bike Stations
- US-04 – View Available Bikes
- US-05 – Rent a Bike Using QR Code
- US-06 – View Active Rental
- US-07 – Return a Bike
- US-08 – Pay Rental Fee
- US-14 – Monitor Bike Stations

### Medium Priority – Should Have

- US-09 – View Rental History
- US-10 – Reserve a Bike
- US-11 – Cancel Reservation
- US-12 – Report a Damaged Bike
- US-13 – Receive Rental Notifications
- US-15 – Manage Bike Maintenance

---

# 9. Үндсэн хэрэглэгчийн урсгал

```text
Бүртгүүлэх
    ↓
Нэвтрэх
    ↓
Газрын зураг харах
    ↓
Зогсоол сонгох
    ↓
Сул дугуй сонгох
    ↓
QR код уншуулах
    ↓
Түрээс эхлэх
    ↓
Хугацаа / төлбөр хянах
    ↓
Дугуй буцаах
    ↓
Төлбөр төлөх
    ↓
Түрээсийн түүх харах
```

---

# 10. GitHub Project

Product Backlog-ийн ажлын төлөвийг дараах байдлаар удирдана.

| Status | Тайлбар |
|---|---|
| Todo | Хийгдэж эхлээгүй User Story |
| In Progress | Хөгжүүлэлт хийгдэж байгаа User Story |
| Done | Хөгжүүлж, шалгаж дууссан User Story |

---

# 11. Дүгнэлт

Энэхүү лабораторийн ажлаар **Нийтийн дугуй түрээсийн систем (Bike Sharing App)** төслийн зорилго, хэрэглэгчид, хамрах хүрээ болон үндсэн функцуудыг тодорхойлов.

Хэрэглэгчдийн хэрэгцээнд тулгуурлан нийт **15 User Story** боловсруулж, Product Backlog үүсгэн Priority тодорхойлов.

User Story бүрийг **Independent, Negotiable, Valuable, Estimable, Small, Testable (INVEST)** зарчмын дагуу шалгасан.

Мөн User Story бүрт Acceptance Criteria тодорхойлсноор хөгжүүлэлт болон тестийн үед тухайн шаардлага биелсэн эсэхийг шалгах боломжтой болсон.
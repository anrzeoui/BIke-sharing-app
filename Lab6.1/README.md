# Лаборатори 6 — Git Branching, Merge Conflict, Code Review

**CLO4 · Баг-17 · Шинэ 16 лабораторийн зааврын 8-р хуудас.**

Энэ ажил нь Git-ийн branch/conflict/review дасгал. Програмын бүртгэл/нэвтрэлт,
TDD, CI хэрэгжүүлэх өмнөх буруу материалын ажлыг энэ branch-д оруулаагүй.

## 1. Гүйцэтгэсэн ажил

| Зааврын алхам | Бодит төлөв |
|---|---|
| 2 feature branch | `feature/greeting-name`, `feature/greeting-safety` үүссэн |
| Ижил мөрийг өөрчлөх | `Lab6/greeting.py`-ийн greeting return мөрийг хоёр өөрөөр өөрчилсөн |
| Commit түүх | Feature тус бүр initial + техникийн review-ийн дараах fix commit-той |
| Санаатай conflict | Feature A-г main-д нэгтгэсний дараа main-ийг B рүү merge хийхэд бодитоор үүссэн |
| Conflict шийдвэрлэх | A-ийн төслийн нэр/нэртэй мэндчилгээ/CLI, B-ийн safety message/helper бүгдийг хадгалсан |
| Main руу merge | Хоёр feature branch **локал main**-д `--no-ff` merge хийгдсэн |
| Техникийн review | 2 + 2 тодорхой санал, тус бүрийн fix commit ба шалгалт байна |
| GitHub PR/comment | **Үүсээгүй** — интеграцийн write API 403 буцаасан |
| Хосын бодит review | **Хийгдээгүй** — нэг автомат туслах, нэг Git зохиогчоор локал дасгал хийсэн |

## 2. Branch ба commit

| Branch/commit | Үүрэг |
|---|---|
| `feature/lab5-uml-redo` / `729c20b` | Шинэ Lab 5 PDF/draw.io, Lab 6 greeting-ийн нийтлэг суурь |
| `feature/greeting-name` / `5fb9c0c` | Нэр болон төслийн танилцуулгатай greeting |
| `5f4adf2` | Хоосон/зайтай нэр, CLI name-ийн review засвар |
| `feature/greeting-safety` / `e386a3e` | Ижил мөр дээр өөр аюулгүй аяллын уриа |
| `d3f9598` | Нэрийг хадгалах, safety_note-г CLI-д харуулах review засвар |
| `ffd05f5` | Main-тай үүссэн conflict-ийг шийдсэн 2-parent merge commit |
| `21564e3`, `6555231` | Локал main дахь Feature A, B-ийн merge commit |

Эдгээр нь бодит локал commit-ууд; өөр хүний нэрээр co-author эсвэл review зохиогоогүй.

## 3. Conflict хэрхэн үүссэн бэ?

Хоёр branch ижил нийтлэг сууриас эхэлсэн. A нь `return` мөрийг төслийн мэндчилгээ,
B нь аюулгүй аяллын уриа болгосон. A-г main-д нэгтгэсний дараа B дээр:

```bash
git switch feature/greeting-safety
git merge --no-ff main
```

Git exit code **1**, `CONFLICT (content)`, `Lab6/greeting.py`-ийн index stage 1/2/3
гэсэн бодит төлөвийг [conflict-before.json](evidence/conflict-before.json)-д хадгалсан.
`<<<<<<< HEAD`, `=======`, `>>>>>>> main` marker-уудыг тэр JSON-ийн string дотроос үзэж болно.

Зөвхөн `ours` эсвэл `theirs`-ийг бүхэлд нь аваагүй. Хоёр feature-ийн зорилгыг хадгалсан
нэгдсэн return текст, нэр боловсруулах код, CLI болон safety_note()-ийг үлдээж commit хийсэн.

```bash
git add Lab6/greeting.py
git commit -m "merge(lab6): resolve the greeting conflict preserving both features"
git switch main
git merge --no-ff feature/greeting-safety
```

## 4. Шалгалт ба нотолгоо

- [Git graph](evidence/git-graph.txt) — feature, fix, merge commit-уудын snapshot.
- [Conflict-ийн өмнөх төлөв](evidence/conflict-before.json) — бодит Git output, гурван index stage, marker-тай файл.
- [Conflict-ийн дараах шалгалт](evidence/conflict-after.json) — unmerged file байхгүй, хоёр feature хадгалагдсан.
- [Техникийн review-ийн 4 санал](review-notes.md) — аль асуудлыг ямар fix commit зассаныг тайлбарласан.
- [Lab 2–4-ийн тусдаа review](lab2-4-review.md) — эх файлуудыг засварлаагүй.

```bash
python3 Lab6/greeting.py "Ө. Анар"
python3 Lab6/check_preserved.py
git log --graph --oneline --decorate --all
```

Шалгасан зан төлөв: хоосон болон зөвхөн зайтай нэр; нэрийн trim; Монгол нэр; хоёр талын
мэдээлэл хадгалагдах; CLI-д нэр болон safety note харагдах; import үед stdout гарахгүй байх.

## 5. Remote ба хосын review — үлдсэн шаардлага

GitHub репог унших боломжтой боловч `create_blob` нь HTTP **403**, **Resource not accessible by integration**
буцаасан. Иймээс remote branch, PR, comment, remote main merge-г болсон гэж тайлагнаагүй.
Суусан нэмэлт байгаа нь write scope бүрдсэн гэсэн үг биш.

[GitHub-д үргэлжлүүлэх заавар](publish.md) болон гурван бэлэн PR тайлбар дагалдана.
Хосын хоёр гишүүн өөрийн аккаунтаар нэг нэгнийхээ PR-д хамгийн багадаа 2 бодит, хэрэгтэй
comment бичиж, саналыг шийдвэрлэсний дараа remote main руу merge хийх шаардлагатай.
Техникийн туслахын 4 санал нь энэ хүний оролцооны шалгуурыг орлохгүй.

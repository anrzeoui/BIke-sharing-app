# Lab 6 — бодит remote PR review-г гүйцээх

Одоогийн GitHub репод зөвхөн `main` branch, **0 PR** байна. `evidence/` дахь
conflict болон review нь локал дасгалын snapshot. Эдгээрийг хоёр хүний
GitHub PR review болсон мэт тайлагнахгүй.

## Багийн хоёр хүний хийх ажил

1. Шинэ, тус тусдаа `feature/...` branch-ийг `main`-аас үүсгэж, нэг файлын
   нэг мөрийг өөр өөрөөр өөрчлөн тус тусдаа commit/push хийнэ. Хүн бүр
   өөрийн GitHub бүртгэлээр ажиллана.
2. Эхний branch-ийн PR-ийг `main` руу нээж, хамтрагч нь кодын мөр дээр
   **дор хаяж 2 бодит, хэрэгтэй review comment** бичнэ. Саналын дагуу
   зассан commit push хийж, PR-ийг merge хийнэ.
3. Хоёр дахь branch-ийн PR-ийг нээж, эхний хүн мөн **дор хаяж 2 review
   comment** бичнэ. Шинэ `main`-ийг хоёр дахь branch рүү merge хийгээд
   ижил мөрийн conflict-ийг хамт шийдэж commit/push хийнэ.
4. CI ногоон болсны дараа хоёр дахь PR-ийг merge хийнэ. Хоёр PR URL,
   comment, conflict шийдсэн commit, merge commit, Actions run холбоосыг
   тайланд оруулна.

`feature/greeting-name` зэрэг хуучин локал commit нэрс зөвхөн архивын
баримт юм; тэдгээр branch одоогийн remote-д байхгүй. `main`-д байгаа
`Lab6/greeting.py` аль хэдийн хоёр санааг агуулсан тул шинэ дасгалд
адилхан мөртэй жижиг тусдаа файл эсвэл тохирсон шинэ өөрчлөлт сонгоно.

GitHub plugin branch үүсгэхэд `403 Resource not accessible by integration`
буцаасан. Репод бичих эрхтэй өөрийн `git`/`gh` нэвтрэлтээр дээрх
алхмуудыг хийж, үр дүнг бодит холбоосоор шалгана.

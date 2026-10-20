# GitHub дээр үргэлжлүүлэх

Одоогоор remote руу бичих оролдлого 403 алдаатай. Энэ файл нь хийх дараалал;
PR/comment/remote merge хийгдсэн гэсэн нотолгоо биш.

## 1. Bundle-ээс түүхтэй нь сэргээх

ZIP-ээ задлаад bundle байгаа хавтсаас:

```bash
git clone --branch main bike-sharing-corrected-lab5-6.bundle BIke-sharing-app
cd BIke-sharing-app
git branch local/completed main
git branch feature/lab5-uml-redo origin/feature/lab5-uml-redo
git branch feature/greeting-name origin/feature/greeting-name
git branch feature/greeting-safety origin/feature/greeting-safety
git remote set-url origin https://github.com/anrzeoui/BIke-sharing-app.git
git fetch origin
```

GitHub-д өөрийн баталгаажсан SSH эсвэл credential helper/GitHub CLI орчноор нэвтэрсэн байна.
`local/completed` нь локал нэгтгэсэн үр дүнг хадгална. Remote main-ийг force push хийхгүй.

## 2. Feature branch-уудыг push хийх

```bash
git push origin feature/lab5-uml-redo
git push origin feature/greeting-name
git push origin feature/greeting-safety
```

Дараах PR-уудыг GitHub UI эсвэл GitHub CLI-гаар **дарааллаар** нээж review хийлгэн merge хийнэ:

```bash
gh pr create --base main --head feature/lab5-uml-redo --title "Lab 5: UML ба архитектур" --body-file Lab6/pr-lab5.md
# Эхний PR merge болсны дараа:
gh pr create --base main --head feature/greeting-name --title "Lab 6: Нэртэй мэндчилгээ" --body-file Lab6/pr-greeting-name.md
# Feature A-ийн PR review ба merge дууссаны дараа:
gh pr create --base main --head feature/greeting-safety --title "Lab 6: Safety ба conflict resolution" --body-file Lab6/pr-greeting-safety.md
```

Хоёр хүн нэг нэгнийхээ Lab 6 PR дээр тус бүр 2 бодит comment бичнэ. Саналын дагуу
засвар хийж, шийдвэрээ comment/commit-оор холбоно. Merge хийхдээ **Create a merge commit**
сонговол conflict resolution-ийн түүх хадгалагдана. Squash/rebase нь дасгалын түүхийг хялбаршуулж харуулж болзошгүй.

Локал main дээр merge-үүдийг аль хэдийн хийсэн тул түүнийг remote main руу шууд push хийхийн оронд
дээрх PR дарааллыг ашиглана. Remote дээрх merge commit SHA нь локалаас өөр байж болно.

## 3. Нотолгоо ба тайлангаа оруулах

Гурван PR merge болсны дараа:

```bash
git fetch origin
git switch -c docs/lab6-evidence origin/main
git restore --source=local/completed -- Lab6/README.md Lab6/review-notes.md Lab6/lab2-4-review.md Lab6/publish.md Lab6/pr-lab5.md Lab6/pr-greeting-name.md Lab6/pr-greeting-safety.md Lab6/check_preserved.py Lab6/.gitignore Lab6/evidence
```

Энэ branch дээр бодит PR/comment URL-уудаа тайланд нөхөж, remote төлөвийг шинэчилнэ.
Дараа нь `git add Lab6`, commit, push хийгээд тайлангийн PR нээнэ.
`python3 Lab6/check_preserved.py`-г ажиллуулж Lab 2–4 өөрчлөгдөөгүйг дахин батална.

Хүлээлгэж өгөх эцсийн холбоос нь https://github.com/anrzeoui/BIke-sharing-app —
түүний commit history, Pull requests, хосын бодит comment-үүд харагдаж байх ёстой.
